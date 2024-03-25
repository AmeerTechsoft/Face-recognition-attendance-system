import os
import time
from flask import current_app
from apps.student import blueprint
from flask import render_template, request, redirect, flash, url_for, Response
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps.authentication.models import Student, Lecturer, Admin, Course, AttendanceRecord
from apps.authentication.forms import StudentChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from apps import db
import cv2
from .forms import UpdateImagesForm
from mediapipe import solutions


@blueprint.route('/dashboard')
@login_required
def student_dashboard():
    # Add logic for rendering the student dashboard template
    student_info = Student.query.filter_by(id=current_user.id).first()
    return render_template('student/dashboard.html', student_info=student_info, user = current_user, user_type = "student")

# Change password route for students
@blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required
def student_change_password():
    form = StudentChangePasswordForm()

    if form.validate_on_submit():
        student = Student.query.get(current_user.id)
        old_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password != confirm_password:
            flash("New Password and Confirm Password do not match", "danger")
            return render_template('student/student_change_password.html', form=form, user_type = "student" )
        
        if check_password_hash(student.password, old_password):
            student.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password changed successfully!', "success")
            return redirect(url_for('student_blueprint.student_dashboard'))
        else:
            flash('Incorrect old password. Please try again.', "danger")

    return render_template('student/student_change_password.html', form=form, user_type = "student" )


@blueprint.route('/courses', methods=['GET', 'POST'])
@login_required
def student_courses():
    if request.method == 'POST':
        # Handle form submission to add courses
        course_id = request.form.get('course_id')
        student = current_user  # Assuming the current_user is a student
        course = Course.query.get(course_id)
        if course:
            if course not in student.courses:
                student.courses.append(course)
                db.session.commit()
                flash(f'Course "{course.name}" added successfully!', 'success')
            else:
                flash(f'Course "{course.name}" is already in your selected courses!', 'danger')
        else:
            flash('Course not found!', 'danger')

    # Fetch available courses from the database
    available_courses = Course.query.all()
    
    # Fetch selected courses for the student
    selected_courses = current_user.courses
    
    return render_template('student/courses.html', available_courses=available_courses, selected_courses=selected_courses, user_type="student")


@blueprint.route('/attendance')
@login_required
def student_attendance():
    attendance_records = AttendanceRecord.query.filter_by(student_id=current_user.name).all()
    return render_template('student/attendance.html', attendance_records=attendance_records, user = current_user, user_type = "student")



@blueprint.route('/update-images', methods=['GET', 'POST'])
@login_required
def student_update_images():
    form = UpdateImagesForm()

    if form.validate_on_submit():
        # Initialize MediaPipe face detection model
        face_detection = solutions.face_detection.FaceDetection()

        # Initialize webcam
        cap = cv2.VideoCapture(0)

        # Allow camera to warm up for 5 seconds
        time.sleep(5)

        # Create a folder for the current user if it doesn't exist
        user_folder = os.path.join(current_app.root_path, 'static', 'images', current_user.name)
        os.makedirs(user_folder, exist_ok=True)

        # Capture 20 images
        num_images = 0
        while num_images < 20:
            ret, frame = cap.read()
            if not ret:
                flash("Error capturing images from webcam", "danger")
                break

            # Convert the image to RGB (MediaPipe requires RGB format)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces in the frame
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

                    # Save face images in the user's folder
                    image_path = os.path.join(user_folder, f'{num_images}.jpg')
                    cv2.imwrite(image_path, face)
                    num_images += 1
                    if num_images >= 20:
                        break

            # Display captured frame with detected faces
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                             int(bboxC.width * iw), int(bboxC.height * ih)
                # Draw bounding box around detected face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Show the frame
            cv2.imshow('Captured Image', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()

        flash("Images captured successfully", "success")

    # Fetch images of the user if any
    user_images = []
    user_images_path = os.path.join(current_app.root_path,'static', 'images', current_user.name)
    if os.path.exists(user_images_path):
        user_images = [f for f in os.listdir(user_images_path) if os.path.isfile(os.path.join(user_images_path, f))]
        user_images = [os.path.join('images', current_user.name, img).replace('\\', '/') for img in user_images]


    return render_template('student/update_images.html', user_type="student", user=current_user, form=form, user_images=user_images)

