
from flask import render_template, redirect, request, url_for, current_app, flash, jsonify, Response, session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import date, datetime
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.models import Student, Lecturer, Admin, Course, AttendanceRecord
from apps.authentication.forms import StudentRegistrationForm, LecturerRegistrationForm, StudentLoginForm, LecturerLoginForm, AdminLoginForm, StudentChangePasswordForm, LecturerChangePasswordForm, UploadForm, AttendanceForm
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
import cv2
from werkzeug.utils import secure_filename
import os
import mediapipe as mp
import numpy as np
import torch
import torchvision
from facenet_pytorch import MTCNN
from sklearn.preprocessing import LabelEncoder, Normalizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
import joblib


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@blueprint.route('/')
def route_default():
    return render_template('accounts/home.html')

# Login & Registration

@blueprint.route('/admin', methods=['GET', 'POST'])
def admin_login():
    login_form = AdminLoginForm()  # Assuming you have defined an AdminLoginForm

    if request.method == 'POST' and login_form.validate():
        username = login_form.username.data
        password = login_form.password.data

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_blueprint.dashboard'))

        flash('Invalid username or password', 'danger')
        return render_template('accounts/admin_login.html', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/admin_login.html', form=login_form)

    return redirect(url_for('admin_blueprint.dashboard'))



@blueprint.route('/student/login', methods=['GET', 'POST'])
def student_login():
    login_form = StudentLoginForm()

    if request.method == 'POST' and login_form.validate():
        student_id = login_form.student_id.data
        password = login_form.password.data

        student = Student.query.filter_by(student_id=student_id).first()

        if student and check_password_hash(student.password, password):
            login_user(student)
            return redirect(url_for('student_blueprint.student_dashboard'))

        flash('Invalid email or password', 'danger')
        return render_template('accounts/student_login.html', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/student_login.html', form=login_form)

    return redirect(url_for('student_blueprint.student_dashboard'))


@blueprint.route('/lecturer/login', methods=['GET', 'POST'])
def lecturer_login():
    login_form = LecturerLoginForm()

    if request.method == 'POST' and login_form.validate():
        lecturer_id= login_form.lecturer_id.data
        password = login_form.password.data

        lecturer = Lecturer.query.filter_by(lecturer_id=lecturer_id).first()

        if lecturer and check_password_hash(lecturer.password, password):
            login_user(lecturer)
            return redirect(url_for('lecturer_blueprint.lecturer_dashboard'))

        flash('Invalid email or password', 'danger')
        return render_template('accounts/lecturer_login.html', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/lecturer_login.html', form=login_form, user_type= "lecturer")

    return redirect(url_for('lecturer_blueprint.lecturer_dashboard'))



@blueprint.route('/register/student', methods=['GET', 'POST'])
def register_student():
    form = StudentRegistrationForm()

    if form.validate_on_submit():
        # Check if Student ID is already registered
        existing_student_matric = Student.query.filter_by(student_id=form.student_id.data).first()
        if existing_student_matric:
            flash('Student ID is already registered. Please use a different Student ID.', 'danger')
            return render_template('accounts/student_register.html', success=False, form=form)
        
        existing_student_email = Student.query.filter_by(email=form.email.data).first()
        if existing_student_email:
            flash('Email Address is already registered. Please use a different Email Address.', 'danger')
            return render_template('accounts/student_register.html', success=False, form=form)

        # Save profile picture
        profile_picture = form.profile_picture.data
        profile_image_url = save_profile_picture(profile_picture)

        # Create a new student
        student = Student(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            password= generate_password_hash(form.password.data),
            student_id=form.student_id.data,
            year=form.year.data,
            semester=form.semester.data,
            program=form.program.data,
            profile_image_url=profile_image_url
        )

        db.session.add(student)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return render_template('accounts/student_register.html', success=True, form=form)

    return render_template('accounts/student_register.html', form=form)

@blueprint.route('/register/lecturer', methods=['GET', 'POST'])
def register_lecturer():
    form = LecturerRegistrationForm()

    if form.validate_on_submit():
        # Check if lecturer ID is already registered
        existing_lecturer_id = Lecturer.query.filter_by(lecturer_id=form.lecturer_id.data).first()
        if existing_lecturer_id:
            flash('Lecturer ID is already registered. Please use a different Lecturer ID.', 'danger')
            return render_template('accounts/lecturer_register.html', success=False, form=form)
        
        existing_lecturer_email = Lecturer.query.filter_by(email=form.email.data).first()
        if existing_lecturer_email:
            flash('Email Address is already registered. Please use a different Email Address.', 'danger')
            return render_template('accounts/lecturer_register.html', success=False, form=form)

        # Save profile picture
        profile_picture = form.profile_picture.data
        profile_image_url = save_profile_picture(profile_picture)

        # Create a new lecturer
        lecturer = Lecturer(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            password=generate_password_hash(form.password.data),
            lecturer_id=form.lecturer_id.data,
            profile_image_url=profile_image_url
        )

        db.session.add(lecturer)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return render_template('accounts/lecturer_register.html', success=True, form=form)

    return render_template('accounts/lecturer_register.html', form=form)

def save_profile_picture(profile_picture):
    if profile_picture:
        filename = secure_filename(profile_picture.filename)
        if allowed_file(filename):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_images', filename)
            profile_picture.save(file_path)
            print(filename)
            return os.path.join(f'profile_images/{filename}')
            

    return None



@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.route_default'))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
facenet_model = torchvision.models.inception_v3(pretrained=True)
facenet_model.aux_logits = False  # Disable auxiliary outputs
facenet_model.eval().to(device)


# Initialize MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.9)

# Define function to preprocess face images (with clear resizing)
def preprocess_face(face_image):
    # Resize face image to the input size expected by InceptionResNetV2
    face_image = cv2.resize(face_image, (299, 299))  

    # Convert face image to tensor and normalize 
    face_tensor = torch.tensor(face_image, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0).to(device)

    # InceptionResNetV2 expects values in the range [-1, 1], so normalize accordingly.
    face_tensor = (face_tensor - 127.5) / 128.0

    return face_tensor


# --- Model Building (Saving Embeddings) ---

# Threshold for determining a match
VERIFICATION_THRESHOLD = 1.0

# Function to save user embeddings
def save_embeddings(user_images_path="apps/static/images"):
    users = os.listdir(user_images_path)
    encodings = {}

    for user in users:
        user_encodings = []  
        user_folder = os.path.join(user_images_path, user)

        for image_name in os.listdir(user_folder):
            image_path = os.path.join(user_folder, image_name)
            img = cv2.imread(image_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB

            # Detect faces using MediaPipe
            results = face_detection.process(img_rgb)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = img_rgb.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                                int(bboxC.width * iw), int(bboxC.height * ih)
                    # Adjust face bounding box to cover the entire face
                    x -= int(0.3 * w)
                    y -= int(0.3 * h)
                    w += int(0.4 * w)
                    h += int(0.5 * h)
                    face = img_rgb[max(0, y):min(y + h, ih), max(0, x):min(x + w, iw)]

                    face_tensor = preprocess_face(face)
                    embedding = facenet_model(face_tensor).detach().cpu().numpy()
                    user_encodings.append(embedding) 

        encodings[user] = user_encodings

    joblib.dump(encodings, 'apps/models/encodings.pkl')
    flash('Embeddings Saved!!','success')


@blueprint.route('/build-model', methods=['GET', 'POST'])
@login_required
def build_model(user_images_path="apps/static/images"):
    save_embeddings(user_images_path)
    return render_template('admin/dashboard.html', user_type='admin')    


# --- Face Verification ---

# Load saved embeddings
predicted_user = None

# Initialize MediaPipe face detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.9)

def verify_face(frame):
    encodings = joblib.load('apps/models/encodings.pkl')
    # Convert frame to RGB (if it's not already)
    if frame.shape[2] != 3: 
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        frame_rgb = frame.copy()  

    # Detect faces
    results = face_detection.process(frame_rgb)

    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = frame.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                         int(bboxC.width * iw), int(bboxC.height * ih)
            # Adjust face bounding box to cover the entire face
            x -= int(0.3 * w)
            y -= int(0.3 * h)
            w += int(0.4 * w)
            h += int(0.5 * h)
            face = frame[max(0, y):min(y + h, ih), max(0, x):min(x + w, iw)]

            face_tensor = preprocess_face(face)
            embedding = facenet_model(face_tensor).detach().cpu().numpy()

            is_verified = False

            for user, user_embeddings in encodings.items():
                for saved_embedding in user_embeddings:
                    distance = np.linalg.norm(embedding - saved_embedding)
                    if distance <= VERIFICATION_THRESHOLD:
                        is_verified = True
                        global predicted_user
                        predicted_user = user
                        break  

                if is_verified: 
                    break 

            # Draw bounding box and label 
            if is_verified:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f'Verified: {predicted_user}', (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, 'Unknown', (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    return frame

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = verify_face(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@blueprint.route('/mark', methods=['GET', 'POST'])
def mark():
    form = AttendanceForm()
    courses = Course.query.all()

    if form.validate_on_submit():
        # Retrieve form data
        course_id = form.course_code.data

        global predicted_user
        if predicted_user is None:
            flash('No user recognized!', 'danger')
            return redirect(url_for('authentication_blueprint.mark'))

        # Retrieve the course to get the lecturer_id
        course = Course.query.get(course_id)
        if not course:
            flash('Course not found!', 'danger')
            return redirect(url_for('authentication_blueprint.mark'))

        # Check if attendance for the current day and course already exists
        today_date = date.today()
        existing_attendance = AttendanceRecord.query.filter(
            AttendanceRecord.date == today_date,
            AttendanceRecord.course_id == course.code,
            AttendanceRecord.student_id == predicted_user
        ).first()
        
        if existing_attendance:
            flash('Attendance already marked for today in this course for user! ' + predicted_user, 'danger')
            return redirect(url_for('authentication_blueprint.mark'))

        # Create a new attendance record
        attendance_record = AttendanceRecord(
            student_id=predicted_user,
            course_id=course.code,  # Assuming course code is used for course identification
            date=today_date,
            timestamp=datetime.now(),
            lecturer_id=course.lecturer
        )

        # Add the attendance record to the database
        db.session.add(attendance_record)
        db.session.commit()

        

        flash('Attendance marked successfully! ' + predicted_user, 'success')
        # Clear predicted_user after successful attendance marking
        predicted_user = None
        return redirect(url_for('authentication_blueprint.mark'))
    
    predicted_user = None
    return render_template('accounts/mark.html', form=form, courses=courses)



@blueprint.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')





@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


