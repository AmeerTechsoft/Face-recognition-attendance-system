from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FileField, DateField, DateTimeField, ValidationError
from wtforms.validators import Email, DataRequired, Optional, Regexp
from wtforms.fields import EmailField
from apps.authentication.models import Lecturer, Student, Course

# Student form
class StudentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    student_id = StringField('Student ID', validators=[DataRequired()])
    year = SelectField('Year', choices=[('1', 'Foundation year'), ('2', 'Year 1'), ('3', 'Year 2'), ('4', 'Year 3')], validators=[DataRequired()])
    semester = SelectField('Semester', choices=[('1', 'Fall'), ('2', 'Spring'), ('3', 'Summer')], validators=[DataRequired()])
    program = StringField('Program', validators=[DataRequired()])

    def validate_email(self, field):
        if not field.data.endswith("@stu.Nigeria.co.uk"):
            flash("Email must end with '@stu.Nigeria.co.uk'.",'danger')
            raise ValidationError("Email must end with '@stu.Nigeria.co.uk'.")

# lecturer form
class LecturerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture')
    lecturer_id = StringField('Lecturer ID', validators=[DataRequired()])

    def validate_email(self, field):
        if not field.data.endswith("@lec.Nigeria.co.uk"):
            flash("Email must end with '@lec.Nigeria.co.uk'.",'danger')
            raise ValidationError("Email must end with '@lec.Nigeria.co.uk'.")


# Course form
class CourseForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    code = StringField('Code', validators=[DataRequired()])
    lecturer = SelectField('Lecturer', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.lecturer.choices = [(lecturer.name, lecturer.name) for lecturer in Lecturer.query.all()]
# Attendance record form
class AttendanceRecordForm(FlaskForm):
    student = SelectField('Student ID', coerce=int, validators=[DataRequired()])
    course = SelectField('Course ID', coerce=int, validators=[DataRequired()])
    timestamp = DateTimeField('Timestamp', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    lecturer = SelectField('lecturer ID', coerce=int)

class SearchForm(FlaskForm):
    date = DateField('Date', validators=[Optional()])
    lecturer = SelectField('Lecturer', choices=[], coerce=int, validators=[Optional()])
    student = SelectField('Student', choices=[], coerce=int, validators=[Optional()])
    course = SelectField('Course', choices=[], coerce=str, validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.lecturer.choices = [(lecturer.id, lecturer.name) for lecturer in Lecturer.query.all()]
        self.student.choices = [(student.id, student.name) for student in Student.query.all()]
        self.course.choices = [(course.code, course.name) for course in Course.query.all()]