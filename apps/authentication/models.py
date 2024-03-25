import os
from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship
from apps import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from sqlalchemy.orm import relationship
import hashlib

# Association table for many-to-many relationship between Students and Courses
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

lecturer_courses = db.Table('lecturer_courses',
    db.Column('lecturer_id', db.Integer, db.ForeignKey('lecturers.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
)

# User types with specific attributes
class Student(db.Model, UserMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    dob = db.Column(db.Date)
    password = db.Column(db.String(128), nullable=False)
    profile_image_url = db.Column(db.String(255))
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    program = db.Column(db.String(64))
    courses = db.relationship('Course', secondary=student_courses, backref=db.backref('students', lazy='dynamic'))
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    def __init__(self, name, email, dob, password, profile_image_url, student_id, year, semester, program):
        self.name = name
        self.email = email
        self.dob = dob
        self.password = password  # Hash the password
        self.profile_image_url = profile_image_url
        self.student_id = student_id
        self.year = year
        self.semester = semester
        self.program = program


    @property
    def image_url(self):
        if self.profile_image_url:
            # Assuming you have a static route set up for profile images
            return url_for('static', filename=self.profile_image_url)
        # Provide a default image URL or handle the case when no image is available
        return url_for('static', filename='apps/static/assets/img/logo-ct-dark.png')
    
    @image_url.setter
    def image_url(self, value):
        # This setter is required by Flask-Login
        pass

    # Add other methods as needed

class Lecturer(db.Model, UserMixin):
    __tablename__ = 'lecturers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    dob = db.Column(db.Date)
    password = db.Column(db.String(128), nullable=False)
    profile_image_url = db.Column(db.String(255))
    lecturer_id = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, name, email, dob, password, lecturer_id, profile_image_url):
        self.name = name
        self.email = email
        self.dob = dob
        self.password = password # Hash the password
        self.profile_image_url = profile_image_url
        self.lecturer_id = lecturer_id

    @property
    def image_url(self):
        if self.profile_image_url:
            # Assuming you have a static route set up for profile images
            return url_for('static', filename=self.profile_image_url)
        # Provide a default image URL or handle the case when no image is available
        return url_for('static', filename='apps/static/assets/img/logo-ct-dark.png')
    
    @image_url.setter
    def image_url(self, value):
        # This setter is required by Flask-Login
        pass
class Admin(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}')"

    # Set password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Check password
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    lecturer = db.Column(db.String(100), nullable=False)
    
    def __init__(self, name, code, lecturer):
        self.name = name
        self.code = code
        self.lecturer = lecturer

class AttendanceRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('lecturers.id'), nullable=True)

    def __init__(self, student_id, course_id, date, timestamp, lecturer_id=None):
        self.student_id = student_id
        self.course_id = course_id
        self.date = date
        self.timestamp = timestamp
        self.lecturer_id = lecturer_id



@login_manager.user_loader
def load_user(user_id):
    # Load user from Student, Lecturer, or Admin model based on user_id
    user = Student.query.get(int(user_id))
    if not user:
        user = Lecturer.query.get(int(user_id))
        if not user:
            user = Admin.query.get(int(user_id))
    return user

@login_manager.request_loader
def load_user_from_request(request):
    email = request.form.get('email')
    username = request.form.get('username')
    if email or username:
        # Check if the email belongs to a student, lecturer, or admin
        student = Student.query.filter_by(email=email).first()
        if student:
            return student
        lecturer = Lecturer.query.filter_by(email=email).first()
        if lecturer:
            return lecturer
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            return admin
    # If no user is found, return None
    return None
