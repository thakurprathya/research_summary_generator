import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, render_template, flash

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('pages/index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            df = pd.read_excel(file)
            # processing of file input data
            return {'message': 'File Saved Successfuly'}, 200
    return {'error': 'Invalid file type or missing file'}, 400

@app.route('/download')
def download():
    return render_template('pages/download.html')

if __name__ == '__main__':
    app.run(debug=True)