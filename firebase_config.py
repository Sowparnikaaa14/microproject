import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase

# Firebase Admin SDK initialization
cred = credentials.Certificate("serviceAccountKey.json")  # You'll need to download this from Firebase
firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()

# Pyrebase Configuration
firebase_config = {
    apiKey: "AIzaSyBeyeEB27ybXZJNU-uyf2RAw2MFWjt52nk",
    authDomain: "trackwise-inventory.firebaseapp.com",
    projectId: "trackwise-inventory",
    storageBucket: "trackwise-inventory.firebasestorage.app",
    messagingSenderId: "647954410139",
    appId: "1:647954410139:web:f0adb8a6ca2446e221743e"
};


firebase = pyrebase.initialize_app(firebase_config)
auth_instance = firebase.auth()