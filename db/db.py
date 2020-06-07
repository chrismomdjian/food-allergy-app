import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "apiKey": os.environ.get('FIREBASE_API_KEY', ''),
    "authDomain": "python-app-test-76c65.firebaseapp.com",
    "databaseURL": "https://python-app-test-76c65.firebaseio.com",
    "projectId": os.environ.get('FIREBASE_PROJECT_ID', ''),
    "storageBucket": "python-app-test-76c65.appspot.com",
    "messagingSenderId": os.environ.get('FIREBASE_MESSAGING_SENDER_ID', ''),
    "appId": os.environ.get('FIREBASE_APP_ID', '')
}

firebase = pyrebase.initialize_app(config)