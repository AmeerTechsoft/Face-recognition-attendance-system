from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField, DateField, ValidationError
from wtforms.validators import Email, DataRequired, Regexp
from flask_wtf.file import FileField, FileRequired
from .models import Student, Lecturer, Admin, Course, AttendanceRecord

# Login Form
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class StudentLoginForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class LecturerLoginForm(FlaskForm):
    lecturer_id = StringField('Lecturer ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Registration Forms
class StudentRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired(message='Date of Birth is required')])
    password = PasswordField('Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    student_id = StringField('Student ID', validators=[DataRequired()])
    year = SelectField('Year', choices=[('Foundation year', 'Foundation year'), ('Year 1', 'Year 1'), ('Year 2', 'Year 2'), ('Year 3', 'Year 3')], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer')], validators=[DataRequired()])
    program = StringField('Programme', validators=[DataRequired()])

    def validate_email(self, field):
        if not field.data.endswith("@stu.Nigeria.co.uk"):
            flash("Email must end with '@stu.Nigeria.co.uk'.",'danger')
            raise ValidationError("Email must end with '@stu.Nigeria.co.uk'.")

class LecturerRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired(message='Date of Birth is required')])
    password = PasswordField('Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    lecturer_id = StringField('Lecturer ID', validators=[DataRequired()])
    
    def validate_email(self, field):
        if not field.data.endswith("@lec.Nigeria.co.uk"):
            flash("Email must end with '@lec.Nigeria.co.uk'.",'danger')
            raise ValidationError("Email must end with '@lec.Nigeria.co.uk'.")

class AdminForm(FlaskForm):
    # Add fields specific to the Admin model if needed
    pass

class StudentChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])

class LecturerChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])

class CourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    code = StringField('Code', validators=[DataRequired()])
    lecturer= StringField('Lecturer', validators=[DataRequired()])

class UploadForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired()])

class AttendanceForm(FlaskForm):
    course_code = SelectField('Course Code', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.course_code.choices = [(course.id, course.code) for course in Course.query.all()]