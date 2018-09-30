from flask import Flask, render_template, request
import os
import cloudstorage as gcs
from google.appengine.api import app_identity

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part.'
        file = request.files.get('file')
        if file.filename == '':
            return 'No file selected.'
        if file:
            #public_url = storage.upload_file(file.read(),file.filename,file.content_type)
            return 'Upload success: '# + public_url
    else:
        return render_template('index.html')