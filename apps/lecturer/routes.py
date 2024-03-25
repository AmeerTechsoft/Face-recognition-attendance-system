from apps.lecturer import blueprint
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps.authentication.models import Student, Lecturer, Admin, AttendanceRecord
from apps.authentication.forms import LecturerChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from apps import db


@blueprint.route('/dashboard')
@login_required
def lecturer_dashboard():
    # Add logic for rendering the lecturer dashboard template
    lecturer_info = Lecturer.query.filter_by(id=current_user.id).first()
    return render_template('lecturer/dashboard.html', user_type = "lecturer", user = current_user, lecturer_info=lecturer_info)

@blueprint.route('/change-password', methods=['GET', 'POST'])
@login_required
def lecturer_change_password():
    form = LecturerChangePasswordForm()

    if form.validate_on_submit():
        lecturer = Lecturer.query.get(current_user.id)
        old_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        if new_password != confirm_password:
            flash("New Password and Confirm Password do not match", "danger")
            return render_template('lecturer/lecturer_change_password.html', form=form, uster_type = "student" )
        

        if check_password_hash(lecturer.password, old_password):
            lecturer.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password changed successfully!', "success")
            return redirect(url_for('lecturer_blueprint.lecturer_dashboard'))
        else:
            flash('Incorrect old password. Please try again.', "danger")

    return render_template('lecturer/lecturer_change_password.html', form=form, user_type = "lecturer")


@blueprint.route('/attendance')
@login_required
def lecturer_attendance():
    lecturer_info = Lecturer.query.filter_by(id=current_user.id).first()
    print(lecturer_info.name)
    lecturer_attendance_records = AttendanceRecord.query.filter_by(lecturer_id=lecturer_info.name).all()
    return render_template('lecturer/attendance.html', attendance_records=lecturer_attendance_records, user = current_user, user_type = "lecturer")
