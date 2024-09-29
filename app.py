import os
import time
import bibtexparser
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
            extension = file.filename.split(".")[-1]

            # testing loading screen
            time.sleep(5)

            # calls to Scrapping functions here
            if(extension == "xlsx"):
                print("xlsx")
            else:
                bib_data = file.read().decode('utf-8')
                bib_database = bibtexparser.loads(bib_data)
                entries = bib_database.entries
                df = pd.DataFrame(entries)

                column_order = ['author', 'year', 'title', 'journal', 'address', 'institution']
                df = df.reindex(columns=column_order)
                print(df.iloc[:, 0]) 

            return jsonify({'redirect': url_for('download')})
        else:
            return jsonify({'error': 'Invalid file type or missing file'}), 400
    return jsonify({'error': 'Invalid request method'}), 400

@app.route('/download')
def download():
    return render_template('pages/download.html')

@app.route('/download-file')
def download_file():
    return send_file('D:\Lang\sih\src\static\\assets\demo_main.xlsx', as_attachment=True)

@app.route('/profile')
def profile():
    faculty = [{
            "author_name": "Dr. Ashish Khanna",
            "institution": "Maharaja Agrasen Institute of Technology",
            "email": "ashishkhanna@mait.edu",
            "address": "12/2 1st Floor, Nehru Enclave East",
            "research": [
                {
                    "title": "Early diagnosis of COVID-19-affected patients based on X-ray and computed tomography images using deep learning algorithm",
                    "year": 2022,
                    "journal": "Journal of COVID-19 diagnosis",
                    "abstract": "The study investigates the use of deep learning algorithms to diagnose COVID-19 from chest X-ray and computed tomography (CT) images, aiming for early detection of the virus. Traditional diagnostic methods, like reverse transcription-polymerase chain reaction (RT-PCR) tests, have limitations in terms of speed and availability. The research proposes a model trained on radiographic data to identify COVID-19 infections with improved accuracy and speed. This automated diagnostic approach has the potential to ease the burden on healthcare systems, particularly in regions with limited testing resources. The model could serve as a supplemental tool to enhance early diagnosis and optimize treatment strategies during the pandemic.",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/32904395/"
                },
                {
                    "title": "A novel deep learning-based multi-model ensemble method for the prediction of neuromuscular disorders",
                    "year": 2021,
                    "journal": "Journal of neuromuscular disorders",
                    "abstract": "This study proposes a novel deep learning-based multi-model ensemble method for predicting neuromuscular disorders. The approach combines the strengths of multiple deep learning models to improve the accuracy of predicting these complex disorders. The ensemble method leverages the strengths of convolutional neural networks (CNNs), recurrent neural networks (RNNs), and long short-term memory (LSTM) networks to analyze various data types, including medical images, clinical data, and genomic data. The proposed method is evaluated on a dataset of patients with neuromuscular disorders and demonstrates superior performance compared to individual models. The results show improved accuracy, sensitivity, and specificity in predicting neuromuscular disorders, highlighting the potential of this approach in clinical practice. However, please note that the article has been retracted, indicating that the findings may not be reliable or valid.",
                    "link": "https://www.researchgate.net/publication/327100282_RETRACTED_ARTICLE_Usability_feature_extraction_using_modified_crow_search_algorithm_a_novel_approach"
                },
                {
                    "title": "Enhancing Consumer Electronics in Healthcare 4.0: Integrating Passive FBG Sensor and IoMT Technology for Remote HRV Monitoring",
                    "year": 2024,
                    "journal": "Journal of Healthcare Electronics",
                    "abstract": "This study explores the integration of passive Fiber Bragg Grating (FBG) sensors and Internet of Medical Things (IoMT) technology to enhance remote heart rate variability (HRV) monitoring in healthcare. The proposed system utilizes FBG sensors to measure physiological parameters, such as heart rate and blood pressure, and transmits the data to a cloud-based platform via IoMT technology. The system enables real-time remote monitoring of HRV, allowing for early detection of cardiovascular diseases and stress-related disorders. The authors demonstrate the feasibility and accuracy of the proposed system, highlighting its potential to revolutionize remote healthcare monitoring. The study contributes to the advancement of consumer electronics in healthcare, enabling personalized and preventive medicine.",
                    "link": "https://www.researchgate.net/publication/382087783_Enhancing_Consumer_Electronics_in_Healthcare_40_Integrating_Passive_FBG_Sensor_and_IoMT_Technology_for_Remote_HRV_Monitoring"
                },
                {
                    "title": "Robot-Assisted Video Endoscopic Inguinal Lymph Node Dissection for Penile Cancer: An Indian Multicenter Experience",
                    "year": 2024,
                    "journal": "Journal of Penile Cancer",
                    "abstract": "This study investigates the effects of a mindfulness-based stress reduction (MBSR) program on symptoms of anxiety and depression in patients with chronic pain. A randomized controlled trial was conducted, with 100 participants assigned to either an MBSR group or a wait-list control group. The MBSR program consisted of eight weekly sessions, and participants' symptoms of anxiety and depression were assessed at pre-intervention, post-intervention, and follow-up. The results show that the MBSR group demonstrated significant reductions in symptoms of anxiety and depression compared to the control group. Additionally, the MBSR group showed improvements in sleep quality and life satisfaction. The study concludes that MBSR is a effective intervention for reducing symptoms of anxiety and depression in patients with chronic pain, and highlights the importance of mindfulness-based interventions in pain management.",
                    "link": "https://pubmed.ncbi.nlm.nih.gov/38661519/"
                }]
        },
        {
            "author_name": "Dr. John Doe",
            "institution": "Indian Institute of Technology",
            "email": "john.doe@iit.edu",
            "address": "456 Innovation Blvd, Tech Town, TT 12345",
            "research": [
                {
                    "title": "Machine Learning for Autonomous Systems",
                    "year": 2020,
                    "journal": "Journal of Robotics",
                    "abstract": "",
                    "link": "http://example.com/ml-autonomous-systems"
                },
                {
                    "title": "Optimization Techniques for AI Models",
                    "year": 2021,
                    "journal": "Journal of AI Optimization",
                    "abstract": "",
                    "link": "http://example.com/optimization-techniques"
                }]
        },
        {
            "author_name": "Dr. Emma Johnson",
            "institution": "Delhi Technological University",
            "email": "emma.johnson@dtu.edu",
            "address": "789 Academic Way, Science Park, SP 98765",
            "research": [
                {
                    "title": "Neural Networks for Financial Forecasting",
                    "year": 2022,
                    "journal": "Journal of Financial Data Science",
                    "abstract": "",
                    "link": "http://example.com/neural-networks-financial-forecasting"
                },
                {
                    "title": "AI in Healthcare Diagnostics",
                    "year": 2019,
                    "journal": "Healthcare AI Journal",
                    "abstract": "",
                    "link": "http://example.com/ai-healthcare-diagnostics"
                },
                {
                    "title": "Reinforcement Learning for Game AI",
                    "year": 2021,
                    "journal": "Journal of Game Theory and AI",
                    "abstract": "",
                    "link": "http://example.com/rl-game-ai"
                }]
        },
        {
            "author_name": "Dr. William Taylor",
            "institution": "Birla Institute of Technology and Science",
            "email": "william.taylor@bits.edu",
            "address": "321 Scholar Drive, Knowledge City, KC 65432",
            "research": [
                {
                    "title": "Quantum Computing for Cryptography",
                    "year": 2021,
                    "journal": "Journal of Quantum Research",
                    "abstract": "",
                    "link": "http://example.com/quantum-computing-cryptography"
                },
                {
                    "title": "Big Data Analytics for Social Media",
                    "year": 2022,
                    "journal": "Journal of Data Science",
                    "abstract": "",
                    "link": "http://example.com/big-data-social-media"
                },
                {
                    "title": "AI-driven Predictive Maintenance",
                    "year": 2020,
                    "journal": "Journal of Industrial AI",
                    "abstract": "",
                    "link": "http://example.com/ai-predictive-maintenance"
                }]
        },
        {
            "author_name": "Dr. Sarah Lee",
            "institution": "National Institute of Technology",
            "email": "sarah.lee@nit.edu",
            "address": "987 Technology Blvd, Tech City, TC 87654",
            "research": [
                {
                    "title": "Blockchain for Secure Transactions",
                    "year": 2021,
                    "journal": "Journal of Blockchain and Cryptography",
                    "abstract": "",
                    "link": "http://example.com/blockchain-secure-transactions"
                },
                {
                    "title": "AI Applications in Smart Cities",
                    "year": 2023,
                    "journal": "Journal of Smart Systems",
                    "abstract": "",
                    "link": "http://example.com/ai-smart-cities"
                }]
        }]

    # Sorting the research list by year in descending order
    faculty['research'] = sorted(faculty['research'], key=lambda x: x['year'], reverse=True)

    # Extract unique years
    years = sorted(set(research['year'] for research in faculty['research']), reverse=True)

    return render_template('pages/profile.html', faculty=faculty, years=years)


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