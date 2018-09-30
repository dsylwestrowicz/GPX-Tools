from flask import Flask, render_template, request
import logging
import io, os
import cloudstorage as gcs
import MoveGPSData
import parse_gpx
import generate_path_data
import copy
from google.appengine.api import app_identity

app = Flask(__name__)

# Index
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part.'
        infile = request.files['file']
        if infile.filename == '':
            return 'No file selected.'
        if infile:
            inpath = '/' + os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name()) + '/input/current.gpx'
            outpath = '/' + os.environ.get('BUCKET_NAME',app_identity.get_default_gcs_bucket_name()) + '/output/UpdatedTracks.gpx'
            gcs_file = gcs.open(inpath,'w',content_type='application/gpx+xml',options={'x-goog-acl': 'public-read'})
            gcs_file.write(infile.read())
            gcs_file.close()
            cloudReadFile = gcs.open(inpath)
            try:
               gcs.delete(outpath)
            except:
               pass
            cloudWriteFile = gcs.open(outpath,'w',content_type='application/gpx+xml',options={'x-goog-acl': 'public-read'})
            # Process
            activity = parse_gpx.Activity(cloudReadFile)
            coordinates = activity.getCoordinates()
            new_coordinates = copy.deepcopy(coordinates)
            i = 0
            total_pts_changed = 0
            query = generate_path_data.Overpass_Query(coordinates[0][0], coordinates[0][1])
            paths, nodes = query.getPaths()

            for coordinate in coordinates:
                move = MoveGPSData.MoveGPSData(10, 1.6, 16, coordinates)
                a = paths, nodes
                move.import_paths_and_coors(a)
                new_coordinates[i], point_change = move.move_points(i)
                total_pts_changed += point_change
                i = i + 1
            activity.modifyCoordinates(new_coordinates, cloudWriteFile)

            cloudReadFile.close()
            cloudWriteFile.close()
            return render_template('index.html',fileUploaded=True)
    else:
        return render_template('index.html',fileUploaded=False)