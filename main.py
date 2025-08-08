import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from functools import wraps
from database import get_db
import json
import pandas as pd
import pickle
import numpy as np
from datetime import datetime
import google.generativeai as genai
import atexit
from PIL import Image
import ast  # Add this at the top of the file with other imports
from werkzeug.utils import secure_filename
from constants import SYMPTOMS_DICT, DISEASES_LIST

# Set up the model configuration first
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Add the doctor's context
DOCTOR_CONTEXT = """You are Dr.AI, a highly skilled and empathetic medical AI assistant. Your role is to:
1. Listen carefully to patients' symptoms and concerns
2. Ask relevant follow-up questions to gather more information
3. Provide preliminary analysis of possible conditions
4. Offer general health advice and suggestions
5. Always remind patients that this is AI-generated advice and they should consult with a human doctor for proper diagnosis
6. Be professional but warm and supportive in your communication
7. Never prescribe medication or make definitive diagnoses
8. Use clear, simple language that patients can understand
9. Show empathy and understanding towards patient concerns

Remember to maintain medical ethics and privacy standards in all interactions."""

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    chat = model.start_chat(history=[])
    chat.send_message(DOCTOR_CONTEXT)
except Exception as e:
    print(f"Error initializing Gemini AI: {str(e)}")
    chat = None

# Cleanup function
def cleanup():
    try:
        global chat, model
        if chat is not None:
            # Clean up Gemini resources
            chat = None
        if model is not None:
            model = None
        # Force garbage collection
        import gc
        gc.collect()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# Register cleanup function
atexit.register(cleanup)

# flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
app.secret_key = SECRET_KEY

# Configure upload folder
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure static folder exists
if not os.path.exists('static'):
    os.makedirs('static')
if not os.path.exists('static/img'):
    os.makedirs('static/img')

# Initialize Supabase client
supabase = get_db()

# Custom Jinja2 filters
@app.template_filter('format_date')
def format_date(date_str):
    if not date_str:
        return ''
    try:
        if isinstance(date_str, str):
            date = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            return date.strftime('%Y-%m-%d')
        return date_str
    except:
        return date_str

@app.template_filter('day_is_today')
def day_is_today(date_str):
    if not date_str:
        return False
    try:
        if isinstance(date_str, str):
            date = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
        else:
            date = date_str
        today = datetime.now()
        return date.date() == today.date()
    except:
        return False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Check if user is admin
        user_id = session['user_id']
        profile = supabase.table('profiles').select("*").eq('id', user_id).execute()
        
        if not profile.data or profile.data[0].get('role') != 'admin':
            flash('Unauthorized access', 'error')
            return redirect(url_for('index'))
            
        return f(*args, **kwargs)
    return decorated_function

from ml_utils import get_predicted_value, get_recommendations

# Helper function to standardize symptom processing
def process_symptoms(symptoms_input):
    """
    Standardize symptom processing from various input formats.
    Args:
        symptoms_input: Can be string, list, or None
    Returns:
        list: Cleaned and validated list of symptoms
    """
    if not symptoms_input:
        return []
        
    # If already a list, clean it
    if isinstance(symptoms_input, list):
        return [s.strip() for s in symptoms_input if s.strip() in SYMPTOMS_DICT]
        
    # If string, try to parse as JSON first
    if isinstance(symptoms_input, str):
        try:
            # Try to parse as JSON array
            symptoms = json.loads(symptoms_input)
            if isinstance(symptoms, list):
                return [s.strip() for s in symptoms if s.strip() in SYMPTOMS_DICT]
        except json.JSONDecodeError:
            # If not JSON, split by comma
            symptoms = [s.strip() for s in symptoms_input.split(',')]
            return [s for s in symptoms if s in SYMPTOMS_DICT]
    
    return []

# creating routes========================================


@app.route("/")
def index():
    return render_template("index.html")

# Define a route for the home page
@app.route('/predict', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        try:
            # Get symptoms from the form
            symptoms_raw = request.form.get('symptoms')
            symptoms = process_symptoms(symptoms_raw)
            
            if not symptoms:
                flash('Please select valid symptoms', 'error')
                return render_template('diagnosis.html', symptoms=list(SYMPTOMS_DICT.keys()))
            
            # Get prediction
            predicted_disease = get_predicted_value(symptoms)
            
            # Get recommendations
            dis_des, precautions, medications, rec_diet, workout = get_recommendations(predicted_disease)
            
            # Save diagnosis to database
            diagnosis_data = {
                'user_id': session['user_id'],
                'symptoms': format_for_db(symptoms),
                'disease': predicted_disease,
                'medications': format_for_db(medications if medications else []),
                'diet': format_for_db(rec_diet if rec_diet else []),
                'workout': workout if workout else '',
                'precautions': format_for_db(precautions[0] if precautions else []),
                'status': 'pending'
            }
            
            try:
                result = supabase.table('diagnoses').insert(diagnosis_data).execute()
                if result.data:
                    flash('Diagnosis saved successfully!', 'success')
                else:
                    flash('Error saving diagnosis results', 'error')
            except Exception as e:
                print(f"Error saving diagnosis: {str(e)}")
                flash('Error saving diagnosis results', 'error')
            
            # Format precautions for display
            my_precautions = []
            if precautions and len(precautions) > 0:
                my_precautions = precautions[0]
            
            return render_template('diagnosis.html',
                                symptoms=list(SYMPTOMS_DICT.keys()),
                                predicted_disease=predicted_disease,
                                dis_des=dis_des,
                                my_precautions=my_precautions,
                                medications=medications,
                                my_diet=rec_diet,
                                workout=workout)
        except Exception as e:
            print(f"Error in predict route: {str(e)}")
            flash('Error processing symptoms', 'error')
            return render_template('diagnosis.html', symptoms=list(SYMPTOMS_DICT.keys()))
    
    return render_template('diagnosis.html', symptoms=list(SYMPTOMS_DICT.keys()))



# about view funtion and path
@app.route('/about')
def about():
    return render_template("about.html")
# contact view funtion and path
@app.route('/contact')
def contact():
    return render_template("contact.html")

# developer view funtion and path
@app.route('/developer')
def developer():
    return render_template("developer.html")

# about view funtion and path
@app.route('/blog')
def blog():
    return render_template("blog.html")

@app.route('/diagnosis', methods=['GET', 'POST'])
@login_required
def diagnosis():
    context = {
        'symptoms': list(SYMPTOMS_DICT.keys()),
        'predicted_disease': None,
        'dis_des': None,
        'my_precautions': None,
        'medications': None,
        'diet': None,
        'workout': None,
        'diagnosis_id': None,
        'status': None,
        'doctor_notes': None
    }
    
    if request.method == 'POST':
        try:
            # Get and validate symptoms using the helper function
            symptoms_raw = request.form.getlist('symptoms[]') or request.form.get('symptoms')
            symptoms = process_symptoms(symptoms_raw)
            
            if not symptoms:
                flash('Please select valid symptoms', 'error')
                return render_template('diagnosis.html', **context)
            
            predicted_disease = get_predicted_value(symptoms)
            desc, pre, med, die, wrkout = get_recommendations(predicted_disease)
            
            # Convert pandas Series to Python types and clean data
            desc = desc.iloc[0] if isinstance(desc, pd.Series) and not desc.empty else None
            pre = pre[0] if pre else []
            med = [str(m) for m in med] if med else []
            die = [str(d) for d in die] if die else []
            wrkout = str(wrkout[0]) if isinstance(wrkout, (list, pd.Series)) and wrkout else ''
            
            # Prepare clean diagnosis data
            diagnosis_data = {
                'user_id': session['user_id'],
                'symptoms': format_for_db(symptoms),  # Clean list of symptoms
                'disease': predicted_disease,
                'medications': format_for_db(med),
                'diet': format_for_db(die),
                'workout': wrkout,
                'precautions': format_for_db(pre),
                'status': 'pending',  # Set initial status to pending
                'doctor_id': None,  # No doctor assigned initially
                'doctor_notes': None,
                'created_at': 'now()'
            }
            
            # Save diagnosis
            result = supabase.table('diagnoses').insert(diagnosis_data).execute()
            
            if result.data:
                current_diagnosis = result.data[0]
                context.update({
                    'diagnosis_id': current_diagnosis['id'],  # Make sure this is passed
                    'current_diagnosis': current_diagnosis,
                    'symptoms': symptoms,
                    'predicted_disease': predicted_disease,
                    'dis_des': desc,
                    'my_precautions': pre,
                    'medications': med,
                    'diet': die,
                    'workout': wrkout,
                    'status': 'pending'
                })
                print(f"[DEBUG] Diagnosis created with ID: {current_diagnosis['id']}")  # Debug print
                flash('Diagnosis saved successfully! Please select a doctor for review.', 'success')
            else:
                flash('Error saving diagnosis', 'error')
                
        except Exception as e:
            print(f"Error in diagnosis route: {str(e)}")
            flash(f'Error processing diagnosis: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('diagnosis.html', **context)

# Example function to save diagnosis history
def format_for_db(value):
    """Format values for database storage, ensuring proper JSONB arrays"""
    if value is None:
        return []
    if isinstance(value, str):
        try:
            # Try to parse as JSON
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [value]
        except json.JSONDecodeError:
            return [value]
    if isinstance(value, list):
        return value
    return [str(value)]

def save_diagnosis(user_symptoms, predicted_disease):
    try:
        # Get recommendations
        dis_des, precautions_list, medications_list, diet_list, workout = get_recommendations(predicted_disease)
        
        # Format data properly for database
        data = {
            'user_id': session['user_id'],
            'symptoms': format_for_db(user_symptoms),
            'disease': predicted_disease,
            'medications': format_for_db(medications_list),
            'diet': format_for_db(diet_list),
            'workout': workout[0] if workout else None,
            'precautions': format_for_db(precautions_list[0] if precautions_list else None),
            'status': 'pending'
        }
        
        # Save to database
        result = supabase.table('diagnoses').insert(data).execute()
        return result.data[0] if result.data else None
        
    except Exception as e:
        print(f"Error saving diagnosis: {str(e)}")
        return None

@app.route('/history')
@login_required
def history():
    try:
        # Get query parameters for filtering
        status_filter = request.args.get('status', 'all')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build the diagnoses query with proper join for doctor information
        diagnoses_query = supabase.table('diagnoses').select(
            "*",
            "profiles!diagnoses_doctor_id_fkey(*)"  # This joins with the doctor's profile
        ).eq('user_id', session['user_id'])
        
        # Apply status filter
        if status_filter != 'all':
            diagnoses_query = diagnoses_query.eq('status', status_filter)
        
        # Apply sorting
        if sort_order == 'desc':
            diagnoses_query = diagnoses_query.order(sort_by, desc=True)
        else:
            diagnoses_query = diagnoses_query.order(sort_by)
        
        # Execute diagnoses query
        diagnoses_result = diagnoses_query.execute()
        
        # Get chat reviews with doctor details
        chat_reviews_query = supabase.table('chat_reviews').select(
            "*",
            "profiles!chat_reviews_doctor_id_fkey(*)"  # This joins with the doctor's profile
        ).eq('user_id', session['user_id'])
        
        # Execute chat reviews query
        chat_reviews_result = chat_reviews_query.execute()
        print(f"Chat reviews result: {chat_reviews_result.data}")  # Debug print
        
        # Process dates and get doctor details
        history_data = []
        if diagnoses_result.data:
            for diagnosis in diagnoses_result.data:
                # Convert created_at string to datetime object
                if diagnosis.get('created_at'):
                    try:
                        created_at = datetime.strptime(diagnosis['created_at'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                        diagnosis['created_at'] = created_at
                    except Exception as e:
                        print(f"Date parsing error: {str(e)}")
                
                # Helper function to process JSONB fields
                def process_jsonb_field(field_value):
                    try:
                        if field_value is None:
                            return []
                        if isinstance(field_value, str):
                            return json.loads(field_value)
                        if isinstance(field_value, list):
                            return field_value
                        return [str(field_value)]
                    except Exception as e:
                        print(f"Error processing JSONB field: {str(e)}")
                        return []
                
                # Process all JSONB fields
                diagnosis['symptoms'] = process_jsonb_field(diagnosis.get('symptoms'))
                diagnosis['medications'] = process_jsonb_field(diagnosis.get('medications'))
                diagnosis['diet'] = process_jsonb_field(diagnosis.get('diet'))
                diagnosis['precautions'] = process_jsonb_field(diagnosis.get('precautions'))
                
                # Get doctor details from the joined data
                if diagnosis.get('profiles'):
                    diagnosis['doctor'] = diagnosis['profiles']
                
                history_data.append(diagnosis)
        
        # Process chat reviews
        chat_reviews = []
        if chat_reviews_result.data:
            for review in chat_reviews_result.data:
                # Convert created_at string to datetime object
                if review.get('created_at'):
                    try:
                        created_at = datetime.strptime(review['created_at'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                        review['created_at'] = created_at
                    except Exception as e:
                        print(f"Date parsing error: {str(e)}")
                
                # Get doctor details from the joined data
                if review.get('profiles'):
                    review['doctor'] = review['profiles']
                
                chat_reviews.append(review)
        
        print(f"Processed chat reviews: {chat_reviews}")  # Debug print
        
        return render_template(
            'history.html',
            history=history_data,
            chat_reviews=chat_reviews,
            current_filter=status_filter,
            current_sort=sort_by,
            current_order=sort_order
        )
        
    except Exception as e:
        print(f"Error in history view: {str(e)}")
        flash('Error loading history', 'error')
        return redirect(url_for('index'))

# Add route to get chat review details
@app.route('/chat_review/<review_id>')
@login_required
def get_chat_review(review_id):
    try:
        user_id = session.get('user_id')
        
        # Get the user's role
        user_profile = supabase.table('profiles').select("*").eq('id', user_id).single().execute()
        if not user_profile.data:
            return jsonify({'error': 'User profile not found'}), 404
            
        # Get the chat review
        review = supabase.table('chat_reviews').select("*").eq('id', review_id).single().execute()
        
        if not review.data:
            return jsonify({'error': 'Chat review not found'}), 404
            
        review_data = review.data
        
        # Allow access if user is:
        # 1. The patient who created the review
        # 2. The doctor assigned to the review
        # 3. An admin
        is_owner = review_data['user_id'] == user_id
        is_assigned_doctor = review_data['doctor_id'] == user_id
        is_admin = user_profile.data.get('role') == 'admin'
        
        if not (is_owner or is_assigned_doctor or is_admin):
            return jsonify({'error': 'Unauthorized access'}), 403
            
        return jsonify(review_data)
    except Exception as e:
        print(f"Error getting chat review: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/diagnosis/details/<diagnosis_id>')
@login_required
def diagnosis_details(diagnosis_id):
    # Get diagnosis details
    diagnosis = supabase.table('diagnoses').select("*").eq('id', diagnosis_id).execute()
    
    if not diagnosis.data:
        return jsonify({'error': 'Diagnosis not found'}), 404
        
    diagnosis_data = diagnosis.data[0]
    
    # Get doctor details if assigned
    if diagnosis_data.get('doctor_id'):
        doctor = supabase.table('profiles').select("*").eq('id', diagnosis_data['doctor_id']).execute()
        if doctor.data:
            diagnosis_data['doctor'] = doctor.data[0]
    
    return jsonify(diagnosis_data)

@app.route('/diagnosis/cancel/<diagnosis_id>', methods=['POST'])
@login_required
def cancel_diagnosis(diagnosis_id):
    try:
        # Get the diagnosis
        diagnosis = supabase.table('diagnoses').select("*").eq('id', diagnosis_id).execute()
        
        if not diagnosis.data:
            return jsonify({'error': 'Diagnosis not found'}), 404
            
        # Check if user owns this diagnosis
        if diagnosis.data[0]['user_id'] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
            
        # Check if diagnosis can be cancelled (only pending ones)
        if diagnosis.data[0]['status'] != 'pending':
            return jsonify({'error': 'Only pending diagnoses can be cancelled'}), 400
        
        # Delete the diagnosis
        supabase.table('diagnoses').delete().eq('id', diagnosis_id).execute()
        
        return jsonify({'message': 'Diagnosis cancelled successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        try:
            # Register user with Supabase
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Store additional user data in profiles table
            user_id = response.user.id
            supabase.table('profiles').insert({
                "id": user_id,
                "name": name,
                "email": email
            }).execute()
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            print(f"Attempting login for email: {email}")
            # Authenticate with Supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Store session data
            session['access_token'] = response.session.access_token
            session['refresh_token'] = response.session.refresh_token
            
            # Get user profile data
            user_id = response.user.id
            print(f"User authenticated, fetching profile for ID: {user_id}")
            profile = supabase.table('profiles').select("*").eq('id', user_id).execute()
            
            if profile.data:
                user_data = profile.data[0]
                print(f"User role: {user_data.get('role')}, Verified: {user_data.get('is_verified')}")
                
                # Store user data in session
                session['user_id'] = user_id
                session['name'] = user_data.get('name', '')
                session['email'] = email
                session['role'] = user_data.get('role', 'user')
                session['is_verified'] = user_data.get('is_verified', False)
                
                flash('Login successful!', 'success')
                
                # Redirect based on role
                if user_data.get('role') == 'doctor':
                    if user_data.get('is_verified'):
                        print("Redirecting verified doctor to dashboard")
                        return redirect(url_for('doctor_dashboard'))
                    else:
                        print("Doctor not verified")
                        flash('Your account is pending verification by an admin.', 'warning')
                        return redirect(url_for('index'))
                else:
                    print("Redirecting regular user to index")
                    return redirect(url_for('index'))
            else:
                print("No profile found for user")
                flash('User profile not found', 'error')
                return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Login failed: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Sign out from Supabase
    supabase.auth.sign_out()
    
    # Clear session
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    try:
        user_id = session['user_id']
        # Get user profile from Supabase
        response = supabase.table('profiles').select("*").eq('id', user_id).execute()
        if response.data:
            user_data = response.data[0]
            # Get diagnosis history count
            history_response = supabase.table('diagnoses').select("*", count="exact").eq('user_id', user_id).execute()
            diagnosis_count = len(history_response.data) if history_response.data else 0
            
            return render_template('profile.html', user=user_data, diagnosis_count=diagnosis_count)
        else:
            flash('Profile not found', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    try:
        user_id = session['user_id']
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        age = request.form.get('age')
        gender = request.form.get('gender')
        
        # Update profile in Supabase
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "age": age,
            "gender": gender,
            "updated_at": 'now()'
        }
        
        response = supabase.table('profiles').update(data).eq('id', user_id).execute()
        
        if response.data:
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile', 'error')
            
        return redirect(url_for('profile'))
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('profile'))

# Add doctor registration route
@app.route('/register/doctor', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        license_number = request.form['license_number']
        specialization = request.form['specialization']
        
        try:
            # Register doctor with Supabase
            response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Store doctor data in profiles table
            user_id = response.user.id
            supabase.table('profiles').insert({
                "id": user_id,
                "name": name,
                "email": email,
                "role": "doctor",
                "license_number": license_number,
                "specialization": specialization,
                "is_verified": False  # Requires admin verification
            }).execute()
            
            flash('Doctor registration successful! Please wait for admin verification.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register_doctor.html')

# Add doctor dashboard route
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    try:
        # Get doctor's profile
        doctor_id = session.get('user_id')
        if not doctor_id:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))

        # Get doctor's profile with role verification
        doctor = supabase.table('profiles').select("*").eq('id', doctor_id).single().execute()
        
        if not doctor.data or doctor.data.get('role') != 'doctor':
            flash('Unauthorized access', 'error')
            return redirect(url_for('index'))
            
        if not doctor.data.get('is_verified'):
            flash('Your account is pending verification', 'error')
            return redirect(url_for('index'))

        # Get all diagnoses assigned to the doctor
        diagnoses = supabase.table('diagnoses')\
            .select("*, profiles!diagnoses_user_id_fkey(name)")\
            .eq('doctor_id', doctor_id)\
            .order('created_at', desc=True)\
            .execute()

        # Get all chat reviews assigned to the doctor
        chat_reviews = supabase.table('chat_reviews')\
            .select("*, profiles!chat_reviews_user_id_fkey(name)")\
            .eq('doctor_id', doctor_id)\
            .order('created_at', desc=True)\
            .execute()

        # Process diagnoses data
        processed_diagnoses = []
        for diagnosis in diagnoses.data:
            processed_diagnoses.append({
                'id': diagnosis.get('id'),
                'patient_name': diagnosis.get('profiles', {}).get('name', 'Unknown Patient'),
                'disease': diagnosis.get('disease', 'Unknown Disease'),
                'status': diagnosis.get('status', 'pending'),
                'created_at': diagnosis.get('created_at'),
                'symptoms': diagnosis.get('symptoms', [])
            })

        # Process chat reviews data
        processed_reviews = []
        for review in chat_reviews.data:
            processed_reviews.append({
                'id': review.get('id'),
                'patient_name': review.get('profiles', {}).get('name', 'Unknown Patient'),
                'status': review.get('status', 'pending'),
                'created_at': review.get('created_at')
            })

        # Calculate statistics
        pending_count = len([d for d in processed_diagnoses if d['status'] == 'pending_review'])
        pending_count += len([r for r in processed_reviews if r['status'] == 'pending'])
        
        today = datetime.now().date()
        today_count = len([d for d in processed_diagnoses if datetime.strptime(d['created_at'].split('T')[0], '%Y-%m-%d').date() == today])
        today_count += len([r for r in processed_reviews if datetime.strptime(r['created_at'].split('T')[0], '%Y-%m-%d').date() == today])
        
        unique_patients = set()
        for d in processed_diagnoses:
            if d['patient_name'] != 'Unknown Patient':
                unique_patients.add(d['patient_name'])
        for r in processed_reviews:
            if r['patient_name'] != 'Unknown Patient':
                unique_patients.add(r['patient_name'])
        total_patients = len(unique_patients)
        
        total_items = len(processed_diagnoses) + len(processed_reviews)
        completed_items = len([d for d in processed_diagnoses if d['status'] not in ['pending', 'pending_review']])
        completed_items += len([r for r in processed_reviews if r['status'] != 'pending'])
        completion_rate = int((completed_items / total_items * 100) if total_items > 0 else 0)

        return render_template('doctor_dashboard.html',
                            diagnoses=processed_diagnoses,
                            chat_reviews=processed_reviews,
                            pending_count=pending_count,
                            today_count=today_count,
                            total_patients=total_patients,
                            completion_rate=completion_rate)
                            
    except Exception as e:
        print(f"Error in doctor dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('index'))

# Add diagnosis approval route
@app.route('/doctor/approve/<diagnosis_id>', methods=['POST'])
@login_required
def approve_diagnosis(diagnosis_id):
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = session['user_id']
        
        # Check if user is a doctor and is verified
        profile = supabase.table('profiles')\
            .select("*")\
            .eq('id', user_id)\
            .eq('role', 'doctor')\
            .eq('is_verified', True)\
            .single()\
            .execute()
            
        if not profile.data:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get the diagnosis and verify assignment
        diagnosis = supabase.table('diagnoses')\
            .select("*")\
            .eq('id', diagnosis_id)\
            .single()\
            .execute()
            
        if not diagnosis.data:
            return jsonify({'error': 'Diagnosis not found'}), 404
            
        # Verify this doctor is assigned to this diagnosis
        if diagnosis.data.get('doctor_id') != user_id:
            return jsonify({'error': 'You are not assigned to this diagnosis'}), 403
            
        # Verify diagnosis is in pending_review status
        if diagnosis.data.get('status') != 'pending_review':
            return jsonify({'error': 'This diagnosis is not pending review'}), 400
        
        # Get status and notes from request data
        status = data.get('status')
        notes = data.get('notes')
        
        if not status or not notes:
            return jsonify({'error': 'Status and notes are required'}), 400
            
        # Validate status is one of the allowed values
        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status value'}), 400
        
        # Update diagnosis
        update_data = {
            'status': status,
            'doctor_notes': notes,
            'updated_at': datetime.now().isoformat()
        }
        
        result = supabase.table('diagnoses')\
            .update(update_data)\
            .eq('id', diagnosis_id)\
            .eq('doctor_id', user_id)\
            .execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to update diagnosis'}), 500
            
        return jsonify({
            'message': f'Diagnosis {status} successfully',
            'status': status
        })
        
    except Exception as e:
        print(f"Error in approve_diagnosis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add route for requesting doctor approval
@app.route('/request_approval', methods=['POST'])
@login_required
def request_approval():
    try:
        print("[DEBUG] Starting request_approval")
        print("[DEBUG] Form data:", request.form)
        
        # Get the diagnosis ID and doctor ID from the form
        diagnosis_id = request.form.get('diagnosis_id')
        doctor_id = request.form.get('doctor_id')
        
        print(f"[DEBUG] Received request - diagnosis_id: {diagnosis_id}, doctor_id: {doctor_id}")
        print(f"[DEBUG] User ID: {session.get('user_id')}")
        
        if not diagnosis_id or not doctor_id:
            print("[ERROR] Missing diagnosis ID or doctor ID")
            return jsonify({'error': 'Missing diagnosis ID or doctor ID.'}), 400
        
        # Get the existing diagnosis first
        print(f"[DEBUG] Fetching existing diagnosis for ID: {diagnosis_id}")
        existing_diagnosis = supabase.table('diagnoses')\
            .select('*')\
            .eq('id', diagnosis_id)\
            .eq('user_id', session['user_id'])\
            .single()\
            .execute()
            
        print(f"[DEBUG] Existing diagnosis data: {existing_diagnosis.data}")
        
        if not existing_diagnosis.data:
            return jsonify({'error': 'Diagnosis not found or unauthorized.'}), 404
            
        # Check if diagnosis already has a doctor assigned
        if existing_diagnosis.data.get('doctor_id'):
            return jsonify({'error': 'This diagnosis already has a doctor assigned.'}), 400
        
        # Verify the doctor exists and is verified
        doctor = supabase.table('profiles')\
            .select('*')\
            .eq('id', doctor_id)\
            .eq('role', 'doctor')\
            .eq('is_verified', True)\
            .single()\
            .execute()
            
        if not doctor.data:
            return jsonify({'error': 'Selected doctor is not available.'}), 400
        
        # Update the existing diagnosis with the doctor ID
        update_data = {
            'doctor_id': doctor_id,
            'status': 'pending_review',  # Changed status to be more specific
            'doctor_notes': None,
            'assigned_at': 'now()',
            'updated_at': 'now()'
        }
        
        # Update the diagnosis
        result = supabase.table('diagnoses')\
            .update(update_data)\
            .eq('id', diagnosis_id)\
            .eq('user_id', session['user_id'])\
            .execute()

        if result.data:
            return jsonify({
                'success': True,
                'message': 'Your diagnosis has been submitted for doctor review.'
            })
        else:
            return jsonify({'error': 'Error submitting diagnosis for review.'}), 500
            
    except Exception as e:
        print(f"Error in request_approval: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Admin dashboard route
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        # Get pending doctor verifications
        pending_doctors = supabase.table('profiles').select("*").eq('role', 'doctor').eq('is_verified', False).execute()
        return render_template('admin_dashboard.html', pending_doctors=pending_doctors.data)
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

# Doctor verification route
@app.route('/admin/verify-doctor/<doctor_id>', methods=['POST'])
@admin_required
def verify_doctor(doctor_id):
    try:
        data = request.get_json()
        is_approved = data.get('is_approved', False)
        
        if is_approved:
            # Update doctor's verification status
            supabase.table('profiles').update({
                'is_verified': True
            }).eq('id', doctor_id).execute()
        else:
            # Delete the doctor's account if rejected
            supabase.table('profiles').delete().eq('id', doctor_id).execute()
        
        return jsonify({'message': 'Doctor verification updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add get_available_doctors endpoint
@app.route('/get_available_doctors')
@login_required
def get_available_doctors():
    try:
        # Get all verified doctors from the profiles table
        doctors = supabase.table('profiles')\
            .select('id, name, specialization')\
            .eq('role', 'doctor')\
            .eq('is_verified', True)\
            .execute()
        
        if doctors.data:
            return jsonify({'doctors': doctors.data})
        else:
            return jsonify({'doctors': []})
    except Exception as e:
        print(f"Error getting available doctors: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add the chat route
@app.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Get the response from Gemini
        response = chat.send_message(message)
        
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

# Add the chat approval route
@app.route('/request_chat_approval', methods=['POST'])
@login_required
def request_chat_approval():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        doctor_id = data.get('doctor_id')
        chat_history = data.get('chat_history', [])
        
        if not doctor_id:
            return jsonify({'error': 'Doctor ID is required'}), 400
            
        if not chat_history:
            return jsonify({'error': 'Chat history is required'}), 400
            
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
            
        # Validate doctor exists and is verified
        doctor = supabase.table('profiles').select("*").eq('id', doctor_id).eq('role', 'doctor').eq('is_verified', True).execute()
        if not doctor.data:
            return jsonify({'error': 'Invalid or unverified doctor'}), 400
            
        # Format chat history for storage
        formatted_chat = {
            'user_id': user_id,
            'doctor_id': doctor_id,
            'chat_history': chat_history,
            'status': 'pending',
            'created_at': 'now()',
            'doctor_notes': None
        }
        
        # Save to chat_reviews table
        result = supabase.table('chat_reviews').insert(formatted_chat).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to save chat review'}), 500
            
        return jsonify({
            'success': True,
            'message': 'Chat review request sent successfully',
            'review_id': result.data[0].get('id')
        })
            
    except Exception as e:
        print(f"Error in request_chat_approval: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add route for doctors to review chat histories
@app.route('/doctor/review_chat/<review_id>', methods=['POST'])
@login_required
def review_chat(review_id):
    try:
        data = request.get_json()
        status = data.get('status')
        notes = data.get('notes')
        
        if not status or not notes:
            return jsonify({'error': 'Status and notes are required'}), 400
            
        # Update chat review
        update_data = {
            'status': status,
            'doctor_notes': notes,
            'reviewed_at': 'now()'
        }
        
        result = supabase.table('chat_reviews').update(update_data).eq('id', review_id).execute()
        
        if result.data:
            return jsonify({'success': True, 'message': f'Chat review {status} successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update chat review'}), 500
            
    except Exception as e:
        print(f"Error in review_chat: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add route for assigning doctor
@app.route('/assign_doctor/<diagnosis_id>', methods=['POST'])
@login_required
def assign_doctor(diagnosis_id):
    try:
        data = request.get_json()
        if not data or 'doctor_id' not in data:
            return jsonify({'error': 'Doctor ID is required'}), 400
            
        doctor_id = data['doctor_id']
        
        # Verify the doctor exists and is verified
        doctor = supabase.table('profiles')\
            .select("*")\
            .eq('id', doctor_id)\
            .eq('role', 'doctor')\
            .eq('is_verified', True)\
            .single()\
            .execute()
            
        if not doctor.data:
            return jsonify({'error': 'Invalid or unverified doctor'}), 400
            
        # Get the diagnosis
        diagnosis = supabase.table('diagnoses')\
            .select("*")\
            .eq('id', diagnosis_id)\
            .single()\
            .execute()
            
        if not diagnosis.data:
            return jsonify({'error': 'Diagnosis not found'}), 404
            
        # Check if diagnosis already has a doctor
        if diagnosis.data.get('doctor_id'):
            return jsonify({'error': 'Diagnosis already has an assigned doctor'}), 400
            
        # Update the diagnosis with the new doctor
        update_data = {
            'doctor_id': doctor_id,
            'status': 'pending_review',
            'updated_at': datetime.now().isoformat(),
            'assigned_at': datetime.now().isoformat()
        }
        
        result = supabase.table('diagnoses')\
            .update(update_data)\
            .eq('id', diagnosis_id)\
            .execute()
            
        if not result.data:
            return jsonify({'error': 'Failed to assign doctor'}), 500
            
        return jsonify({
            'message': 'Doctor assigned successfully',
            'doctor_id': doctor_id
        })
        
    except Exception as e:
        print(f"Error in assign_doctor: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add route for unassigning doctor
@app.route('/unassign_doctor/<diagnosis_id>', methods=['POST'])
@login_required
def unassign_doctor(diagnosis_id):
    try:
        # Get the diagnosis
        diagnosis = supabase.table('diagnoses')\
            .select("*")\
            .eq('id', diagnosis_id)\
            .single()\
            .execute()
            
        if not diagnosis.data:
            return jsonify({'error': 'Diagnosis not found'}), 404
            
        # Check if diagnosis has a doctor
        if not diagnosis.data.get('doctor_id'):
            return jsonify({'error': 'No doctor assigned to this diagnosis'}), 400
            
        # Update the diagnosis to remove the doctor
        update_data = {
            'doctor_id': None,
            'status': 'pending',
            'updated_at': datetime.now().isoformat(),
            'assigned_at': None
        }
        
        result = supabase.table('diagnoses')\
            .update(update_data)\
            .eq('id', diagnosis_id)\
            .execute()
            
        if not result.data:
            return jsonify({'error': 'Failed to unassign doctor'}), 500
            
        return jsonify({
            'message': 'Doctor unassigned successfully'
        })
        
    except Exception as e:
        print(f"Error in unassign_doctor: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/radiology', methods=['GET', 'POST'])
@login_required
def radiology():
    if request.method == 'POST':
        if 'xray_image' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('radiology'))
        
        file = request.files['xray_image']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('radiology'))
        
        if file and allowed_file(file.filename):
            try:
                # Save the file temporarily
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # TODO: Add your X-ray analysis logic here
                
                flash('Image uploaded successfully', 'success')
                return redirect(url_for('radiology'))
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'error')
                return redirect(url_for('radiology'))
        else:
            flash('Invalid file type. Please upload an image file (PNG, JPG, JPEG)', 'error')
            return redirect(url_for('radiology'))
    
    return render_template('radiology.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

