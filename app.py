import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, render_template, flash

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('pages/index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            df = pd.read_excel(file)
            data = df.to_json(orient='split')
            return data, 200, {'Content-Type': 'application/json'}
        return {'error': 'Invalid file type or missing file'}, 400

    return render_template('pages/upload.html')

if __name__ == '__main__':
    app.run(debug=True)