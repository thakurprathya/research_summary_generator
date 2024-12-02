import os
import time
import json
import bibtexparser
import pandas as pd
import io
from datetime import datetime
from flask import Flask, render_template, request, render_template, jsonify, url_for, send_file, session
from werkzeug.exceptions import BadRequest
from flask_cors import CORS
from dotenv import load_dotenv
from services.models import add_faculty_to_db, get_allFaculty, get_facultyById
from services.db_config import get_db_connection
from services.utils import encrypt_data, decrypt_data, update_df, df_to_profile, profile_to_df
from services.functions.main import get_publication_link, get_abstract_and_journal

load_dotenv()
secret_key = os.getenv('SECRET_KEY').encode('utf-8')

app = Flask(__name__)
app.secret_key = secret_key
CORS(app)
db, connection_status = get_db_connection()

# Application routes
@app.route('/')
def home():
    return render_template('pages/index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            extension = file.filename.split(".")[-1]

            if(extension == "xlsx"):
                df = pd.read_excel(file)
                df = df.rename(columns={'Faculty Name': 'name', 'Email': 'email', 'Address': 'address', 'Institution': 'institution', 'Year':'year', 'Publication Title': 'publicationTitle'})
                df['journal'] = ''
            else:
                # parsing bib-tex file and creating a dataframe
                bib_data = file.read().decode('utf-8')
                bib_database = bibtexparser.loads(bib_data)
                entries = bib_database.entries
                df = pd.DataFrame(entries)

                column_order = ['author', 'email', 'address', 'institution', 'year', 'title', 'journal']
                for col in column_order:
                    if col not in df.columns:
                        df[col] = ''
                df = df[column_order]
                df = df.rename(columns={'author': 'name', 'title': 'publicationTitle'})

            df['publicationLink'] = ''
            df['abstract'] = ''
            df['name'] = df['name'].astype(str)
            df['publicationTitle'] = df['publicationTitle'].astype(str)
            df = df.dropna(subset=['name', 'publicationTitle'])
            df = df.fillna('')

            # removing duplicates
            df = df.drop_duplicates(subset=['email', 'publicationTitle'], keep='first')

            # updating data for rows where research exists in db
            df = update_df(df)
            
            # populating links only for empty rows
            for idx in df[df['publicationLink'] == ''].index:
                df.at[idx, 'publicationLink'] = get_publication_link(df.at[idx, 'name'], df.at[idx, 'publicationTitle'])
                time.sleep(1)  # Add a delay between requests to avoid rate limiting
            df['publicationLink'] = df['publicationLink'].astype(str)

            # populating abstract and journal only for empty rows
            for idx in df[df['abstract'] == ''].index:
                abstract, journal = get_abstract_and_journal(df.at[idx, 'publicationLink']) if df.at[idx, 'publicationLink'] else ('', '')
                df.at[idx, 'abstract'] = abstract
                df.at[idx, 'journal'] = journal
                time.sleep(1)  # Add a delay between requests to avoid rate limiting

            # creating a list of dictionaries out of a dataframe
            faculty_profiles = df_to_profile(df)

            # Add each faculty profile to the database
            faculty_ids = []
            for profile in faculty_profiles:
                try:
                    response = app.test_client().post('/add_faculty', 
                        json={
                            'name': profile['name'],
                            'email': profile['email'],
                            'address': profile['address'],
                            'institution': profile['institution'],
                            'research': profile['research']
                        },
                        content_type='application/json'
                    )
                    response_data = response.get_json()
                    profile['_id'] = response_data['id']
                    faculty_ids.append(response_data['id'])
                except Exception as e:
                    print(f"Error adding faculty {profile['name']}: {str(e)}")

            # storing information in session
            session['faculty_ids'] = faculty_ids

            return jsonify({'redirect': url_for('download')})
        else:
            return jsonify({'error': 'Invalid file type or missing file'}), 400
    return jsonify({'error': 'Invalid request method'}), 400

@app.route('/download')
def download():
    faculty_ids = session.get('faculty_ids', [])
    faculty_profiles = []

    for id in faculty_ids:
        response = app.test_client().get(f'/get_faculty_by_id/{id}')
        faculty_data = response.get_json()
        if faculty_data:
            if not isinstance(faculty_data, dict):
                faculty_data = json.loads(faculty_data)
            if '_id' in faculty_data:
                faculty_data['encrypted_id'] = encrypt_data(str(faculty_data['_id']))
            faculty_profiles.append(faculty_data)
    
    return render_template('pages/download.html', faculties=faculty_profiles)

@app.route('/download-file')
def download_file():
    faculty_ids = session.get('faculty_ids', [])
    faculty_profiles = []

    # Get faculty profiles
    for id in faculty_ids:
        response = app.test_client().get(f'/get_faculty_by_id/{id}')
        faculty_data = response.get_json()
        if faculty_data:
            if not isinstance(faculty_data, dict):
                faculty_data = json.loads(faculty_data)
            faculty_profiles.append(faculty_data)
    
    df = profile_to_df(faculty_profiles)
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Research Papers')
    output.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'research_papers_{timestamp}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/profile')
def profile():
    id = request.args.get('faculty')
    if id:
        try:
            # decrypting faculty id
            id = id.replace(' ', '+')  # Fix URL-safe base64 padding
            decrypted_id = decrypt_data(id)
            if not isinstance(decrypted_id, str):
                decrypted_id = str(decrypted_id)
        except Exception as e:
            return f"Error decrypting data: {str(e)}", 400
        
        # fetching faculty data from db
        response = app.test_client().get(f'/get_faculty_by_id/{decrypted_id}')
        faculty = response.get_json()
        if faculty and not isinstance(faculty, dict):
            faculty = json.loads(faculty)

        faculty['research'] = sorted(faculty['research'], key=lambda x: x['year'], reverse=True) # Sorting the research list by year in descending order
        years = sorted(set(research['year'] for research in faculty['research']), reverse=True) # Extract unique years

        return render_template('pages/profile.html', faculty=faculty, years=years)
    
    return "No data available", 400


# Database routes
@app.route('/test_connection', methods=['GET'])
def test_connection():
    if db is not None:
        return jsonify({'status': 'success', 'message': connection_status})
    else:
        return jsonify({'status': 'error', 'message': connection_status}), 500

@app.route('/get_all_faculty', methods=['GET'])
def get_all_faculty():
    try:
        faculty_members = get_allFaculty()
        return jsonify(faculty_members)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_faculty_by_id/<faculty_id>', methods=['GET'])
def get_faculty_by_id(faculty_id):
    try:
        faculty = get_facultyById(faculty_id)
        if faculty:
            return jsonify(faculty)
        else:
            return jsonify({'error': 'Faculty not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415
        
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No input data provided")
            
        name = data.get('name')
        research = data.get('research', [])
        email = data.get('email')
        institution = data.get('institution', '')
        address = data.get('address', '')
        if not name or not research or not email or not institution or not address:
            raise BadRequest("Required Inofrmation not present...")
        
        faculty_id = add_faculty_to_db(name, email, address, research, institution)
        return jsonify({'message': 'Faculty member added successfully', 'id': faculty_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)