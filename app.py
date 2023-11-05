from flask import Flask, request, render_template, redirect, url_for
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Replace with your own S3 bucket and region
S3_BUCKET = 'your-s3-bucket'
S3_REGION = 'your-s3-region'

s3 = boto3.client('s3', region_name=S3_REGION)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file:
        try:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                file.filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            return f'File successfully uploaded to S3 bucket {S3_BUCKET}!'
        except NoCredentialsError:
            return 'AWS credentials not available'
    else:
        return 'No file selected'

if __name__ == '__main__':
    app.run(debug=True)
