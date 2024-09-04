from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('pages/index.html')

@app.route('/upload')
def upload():
    return render_template('pages/upload.html')

if __name__ == '__main__':
    app.run(debug=True)