from flask import Flask, render_template, url_for, redirect, request, jsonify, session, send_file, flash
import firebase_admin
from firebase_admin  import credentials , auth, initialize_app, firestore , storage
import pandas as pd
import os
import json
import uuid
from io import BytesIO
import requests
from PIL import Image, ImageDraw , ImageFont
import mimetypes
from functools import wraps


creds = credentials.Certificate('serviceKey.json')
firebase = initialize_app(creds,{
    "Bucket url for firestore storage  remove 'gs:\\' part "
})



firestore_db = firestore.client()

storage_bucket = storage.bucket()

# Defined schema for firebase database
schema = {
    'Cultural Collection': {
        'Cultural Name': {
            'Event Collection': {
                'Event Name': {
                    'template_url': 'string',
                    'Participants Collection': {
                        'UUID': {
                            'name': 'string',
                            'email': 'string',
                            'register_number': 'string',
                            'department': 'string'
                        }
                    }
                }
            }
        }
    }
}

def get_participation_data(email):
    cultural_data = []

    cultural_ref = firestore_db.collection('Cultural Collection')

    cultural_documents = cultural_ref.list_documents()
    cultural_names = [doc.id for doc in cultural_documents]

  
    for cultural_name in cultural_names:
        event_ref = cultural_ref.document(cultural_name).collection('Event Collection')
        event_documents = event_ref.list_documents()
        event_names = [doc.id for doc in event_documents]
        for event_name in event_names:
            doc_ref = event_ref.document(event_name)

            event_data = doc_ref.get().to_dict()

            participants_ref = doc_ref.collection('Participants Collection')

            participant_query = participants_ref.where('email', '==', email).get()

            for participant_doc in participant_query:
                if participant_doc.exists:
                    participant_data = participant_doc.to_dict()

                    # Append required fields to cultural_data list
                    cultural_data.append({
                        'register_number': participant_data.get('register_number', ''),
                        'department': participant_data.get('department', ''),
                        'email': participant_data.get('email', ''),
                        'Name': participant_data.get('Name', ''),
                        "event_name": event_name,
                        "cultural_name":cultural_name,
                        'template_url': event_data.get('template_url', '')
                        
                    })

    return cultural_data

class RetrieveTemplate:
    def __init__(self):
        self.db = firestore.client()

    def url(self, cultural_name, event_name):
        try:
            cultural_ref = self.db.collection('Cultural Collection').document(cultural_name)
            event_ref = cultural_ref.collection('Event Collection').document(event_name)
            doc = event_ref.get()

            if doc.exists:
                template_url = doc.to_dict().get('template_url')
                if not template_url:
                    raise Exception("Template URL not found in document.")
                print(f"Template URL retrieved: {template_url}")
                return template_url
            else:
                raise Exception("Document not found.")
        except Exception as e:
            print("Error retrieving template URL:", e)
            return None

ADMIN_EMAIL = "admin-example@gmail.com" # Replace it with admin email

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = session.get('user_email')
        if user_email != ADMIN_EMAIL:
            return jsonify({"error": "Access denied"}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_certificate(name, cultural_name, event_name):
    try:
        
        rt = RetrieveTemplate()

        # Retrieve template URL
        template_url = rt.url(cultural_name, event_name)
        if not template_url:
            raise ValueError("Template URL is None")

        # Fetch the template image from the URL
        response = requests.get(template_url)
        response.raise_for_status()  # Check if request was successful
        print(f"Template fetched successfully from {template_url}")

        # Load the image
        template = Image.open(BytesIO(response.content))
        print("Template image loaded successfully")

        # Draw text on the image
        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype('arial.ttf', 40)
        font_color = 'black'
        width, height = template.size
        text_length = draw.textlength(name, font=font)
        start_x = (width - text_length) // 2
        draw.text((start_x, (height - 370) // 2), name, fill=font_color, font=font)
        print(f"Text drawn on the image for {name}")

        # Create a BytesIO object to store the certificate image in memory
        buffer = BytesIO()
        template.save(buffer, format='PDF')
        buffer.seek(0)
        print("Certificate saved to buffer successfully")

        return buffer

    except Exception as e:
        print(f"Error generating certificate for {name}: {e}")
        return None

app = Flask(__name__)
app.secret_key = '5a3ebb4a7aa53eb60389ae7a783428caf7425635-2fd7-4f50-b946-c6414bae90aa'

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/register",methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("Name")
        email = request.form.get("Email")
        password = request.form.get("Password")
        try:
            user = auth.create_user(display_name= name,email=email,password=password)
            if user:
                return redirect('/dashboard')  
        except firebase_admin.auth.EmailAlreadyExistsError:
            return jsonify({"error": "The user with the provided email already exists (EMAIL_EXISTS) please return to signup page."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}) , 400
    return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def login():    
    if request.method == "POST":
        email = request.form.get("Email")
        password = request.form.get("Password")

        try:
            user = auth.get_user_by_email(email)
            if email == ADMIN_EMAIL:
                session['user_email'] = email
                return redirect('/admin_page')
            else:
                session['user_email'] = email
                return redirect('/dashboard')
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('user_email', None)
    return redirect('/login')



@app.route("/admin_page",methods = ["POST","GET"])
@admin_required #preventing the url for adminpage based on sessions of the admin email
def admin():
    if request.method == "POST":
        try:
            participants = request.files['participant_name_list']
            event_name = request.form.get("event_name")
            cultural_name = request.form.get("cultural_name")
            certificate_template = request.files['certificate_template']

            cultural_ref = firestore_db.collection('Cultural Collection').document(cultural_name)
            event_ref = cultural_ref.collection("Event Collection").document(event_name)

            if participants.filename != " ":
                participant_df = pd.read_excel(participants,engine="openpyxl")

                participant_collection = event_ref.collection("Participants Collection")

                for index, row in participant_df.iterrows():
                    participant_id = str(uuid.uuid4())
                    participant_data = {
                        "Name":row['name'],
                        "email": row['email'],
                        "register_number": row["register_number"],
                        "department": row['department']
                    }

                    participant_collection.document(participant_id).set(participant_data)

            if certificate_template.filename.strip():
                mimetype, _ = mimetypes.guess_type(certificate_template.filename,strict=True)
                if mimetype != "image/png":
                    return jsonify({"error": "certificate template must be a PNG file"}), 400
                else:

                    template_name = f"{cultural_name}_{event_name}_template.png"

                    blob = storage_bucket.blob(template_name)
                    blob.upload_from_file(certificate_template,content_type="image/png")
                    blob.make_public()

                    event_ref.set({
                        "template_url":blob.public_url
                    })
            
                flash("Data Stored Successfully!!")
                return redirect(url_for('admin'))
        
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return render_template('admin.html')


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    try:
        user_email = session.get('user_email')
        if not user_email:
            return redirect('/login')
            
        participant_data = get_participation_data(user_email)
            
        return render_template('dashboard.html', participation_data=participant_data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route('/download_certificate', methods=['GET'])
def download_certificate():
    try:
        name = request.args.get('name')
        cultural_name = request.args.get('cultural_name')
        event_name = request.args.get('event_name')
        
        if not all([name, cultural_name, event_name]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        certificate_buffer = generate_certificate(name, cultural_name, event_name)
        
        if certificate_buffer:
            return send_file(certificate_buffer, as_attachment=True, download_name=f"{name}_certificate.pdf", mimetype='application/pdf')
        else:
            return jsonify({"error": "Certificate generation failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    app.run(debug=True)