from flask import Flask, request, render_template, redirect, url_for
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# Replace with your own S3 bucket and region
S3_BUCKET = 'your-s3-bucket'
S3_REGION = 'your-s3-region'

s3 = boto3.client('s3', region_name=S3_REGION)

class IPData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), unique=True)
    uploaded_data = db.Column(db.Float, default=0.0)


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
    file = request.files['file']
    client_ip = request.remote_addr
    ip_data = IPData.query.filter_by(ip_address=client_ip).first()
    if not ip_data:
        ip_data = IPData(ip_address=client_ip)
    uploaded_file_size =  # Calculate the size of the uploaded file in GB
    total_uploaded_data = ip_data.uploaded_data + uploaded_file_size
    if file and total_uploaded_data <= 30:
        try:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                file.filename,
                ExtraArgs={'ACL': 'public-read'}
            )
            #applying rate limting here
            ip_data.uploaded_data = total_uploaded_data
            db.session.add(ip_data)
            db.session.commit()
            download_url = get_download_link(file.filename)
            print(download_url)
            return f'File successfully uploaded to S3 bucket {S3_BUCKET}!'
        except NoCredentialsError:
            return 'AWS credentials not available'
    else:
        return 'No file selected'

if __name__ == '__main__':
    app.run(debug=True)
