from flask import Flask, render_template, request
import logging
import os
import cloudstorage as gcs
import webapp2
from google.appengine.api import app_identity

app = Flask(__name__)

# Index
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part.'
        file = request.files['file']
        if file.filename == '':
            return 'No file selected.'
        if file:
            path = '/' + os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name()) + '/input/current.gpx'
            gcs_file = gcs.open(path,'w',content_type='application/gpx+xml')
            gcs_file.write(file.read())
            gcs_file.close()
            return render_template('index.html',fileUploaded=True)
    else:
        return render_template('index.html',fileUploaded=False)

# Download
@app.route('/download')
def download():
    expfile = 1 # GET FILE FROM CLOUD
    return "DOWNLOAD FILE" #send_file(expfile, mimetype='application/gpx+xml', as_attachment=True, attachment_filename='GPSActivity')