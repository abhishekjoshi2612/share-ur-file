from flask import Flask, request, render_template, redirect, url_for
import boto3
from botocore.exceptions import NoCredentialsError
from flask_sqlalchemy import SQLAlchemy
import os
from os.path import splitext
import codecs
import json

data = None
with open('templates//credential.json') as json_file:
    data = json.load(json_file)
# Replace with your own S3 bucket and region
S3_BUCKET = data['S3_BUCKET']
S3_REGION = data['S3_REGION']
access_key = data['access_key']
secret_access_key = data['secret_access_key']

basedir = os.getcwd()
s3 = boto3.client('s3', region_name=S3_REGION,aws_access_key_id= access_key,aws_secret_access_key=secret_access_key)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class IPData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), unique=True)
    uploaded_data = db.Column(db.Float, default=0.0)

basedir = os.path.abspath(os.path.dirname(__file__))

print("program started")
@app.route('/')
def index():
    return render_template('index.html')

def get_download_link(object_key):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET, 'Key': object_key},
        ExpiresIn=3600  # URL expiration time in seconds (adjust as needed)
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file'].read()
    #file = codecs.encode(file, 'utf-8')
    print("got file")
    client_ip = request.remote_addr
    #ip_data = IPData.query.filter_by(ip_address=client_ip).first()
    #if not ip_data:
        #ip_data = IPData(ip_address=client_ip)
    uploaded_file_size =  30
    #total_uploaded_data = ip_data.uploaded_data + uploaded_file_size
    if file :
        try:
            #filename, file_extension = splitext(file.filename)
            #absolute_path = os.path.realpath(file.filename)
            #print(absolute_path)
            #file_path = str(absolute_path)
            #file.save(file_path)
            #absolute_path = os.path.realpath(file.filename)
            print("trying to upload data")
            #print(file.file)
            object_data = None
            '''with open(file, 'rb') as file:
                object_data = file.read() '''
            s3_client = s3
            s3.put_object(Body=file, Bucket=S3_BUCKET, Key='somethin', ContentType='application/x-unknown-content-type')
            #s3..upload_fileobj(, S3_BUCKET_NAME, filename)
            #applying rate limting here
            #ip_data.uploaded_data = total_uploaded_data
            #db.session.add(ip_data)
            #db.session.commit()
            download_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': 'somethin'}, ExpiresIn=3600)
            print(download_url)
            return f'File successfully uploaded to S3 bucket {S3_BUCKET}!'
        except NoCredentialsError:
            return 'AWS credentials not available'
    else:
        return 'No file selected'

if __name__ == '__main__':
    app.run(debug=True)
