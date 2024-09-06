import os
import pandas as pd
from flask import Flask, render_template, request, render_template, jsonify, redirect, url_for, send_file
from werkzeug.exceptions import BadRequest
from services.models import create_faculty, get_all
from services.db_config import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
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
            return jsonify({'redirect': url_for('download')})
        else:
            return jsonify({'error': 'Invalid file type or missing file'}), 400
    return jsonify({'error': 'Invalid request method'}), 400

@app.route('/download')
def download():
    return render_template('pages/download.html')

@app.route('/download-file')
def download_file():
    return send_file('/Users/prathyathakur/Master/Programming/SIH/sih24/flask_app_env/src/static/assets/demo_main.xlsx', as_attachment=True)

# Database routes
@app.route('/test_connection', methods=['GET'])
def test_connection():
    if db is not None:
        return jsonify({'status': 'success', 'message': connection_status})
    else:
        return jsonify({'status': 'error', 'message': connection_status}), 500
    
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
        if not name or not research:
            raise BadRequest("Name and Research is required")
        
        faculty_id = create_faculty(name, research)
        return jsonify({'message': 'Faculty member added successfully', 'id': faculty_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/get_all_faculty', methods=['GET'])
def get_all_faculty():
    try:
        faculty_members = get_all()
        return jsonify(faculty_members)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)