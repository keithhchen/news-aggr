import os
import json
import traceback
from flask import Flask, current_app
from models import db
from utils.main import load_api_key
from controller.youtube_bp import youtube_bp
from controller.artefact_bp import artefact_bp
from controller.publisher_bp import publisher_bp
from middleware.webhook import webhook_middleware

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = load_api_key("database_url")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register webhook middleware
app.after_request(webhook_middleware())

app.register_blueprint(youtube_bp, url_prefix='/youtube')
app.register_blueprint(artefact_bp, url_prefix='/artefact')
app.register_blueprint(publisher_bp, url_prefix='/publisher')

# BUCKET_NAME = 'keith_speech_to_text'
# storage_client = storage.Client()
# bucket = storage_client.bucket(BUCKET_NAME)

# Print all environment variables when the app starts
print("Starting Flask App with the following environment variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")


@app.route('/', methods=['GET'])
def entry():
    return "hello"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

