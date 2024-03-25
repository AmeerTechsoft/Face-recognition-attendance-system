from apps.admin import blueprint
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from .forms import StudentForm, LecturerForm, CourseForm, AttendanceRecordForm, SearchForm
from apps.authentication.models import Student, Lecturer, Course, AttendanceRecord, Admin, student_courses, lecturer_courses
from werkzeug.security import generate_password_hash, check_password_hash
from apps import db


# Admin dashboard route
@blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html', user_type = 'admin')

# Admin view all students route
@blueprint.route('/students')
@login_required
def view_students():
    form = StudentForm()
    students = Student.query.all()
    return render_template('admin/students.html', students=students, user_type = 'admin', form=form)

# Admin add student route
@blueprint.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        new_student = Student(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            password=generate_password_hash(form.password.data),
            profile_image_url=form.profile_picture.data,
            student_id=form.student_id.data,
            year=form.year.data,
            semester=form.semester.data,
            program=form.program.data
        )
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_students'))
    return render_template('admin/students.html', form=form, user_type = 'admin')

# Admin delete student route
@blueprint.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Delete related attendance records
    AttendanceRecord.query.filter_by(student_id=student.id).delete()
    
    # Remove student from related courses
    for course in student.courses:
        course.students.remove(student)
    
    db.session.delete(student)
    db.session.commit()
    
    flash('Student and its related records deleted successfully.', 'success')
    return redirect(url_for('admin_blueprint.view_students'))


# Admin edit student route
@blueprint.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        form.populate_obj(student)
        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_students'))
    return render_template('admin/edit_student.html', form=form, student=student, user_type = 'admin')

# Admin view all Lecturers route
@blueprint.route('/lecturers')
@login_required
def view_lecturers():
    form = LecturerForm()
    lecturers = Lecturer.query.all()
    return render_template('admin/lecturers.html', lecturers=lecturers, user_type = 'admin', form=form)

# Admin add lecturer route
@blueprint.route('/lecturers/add', methods=['GET', 'POST'])
@login_required
def add_lecturer():
    form = LecturerForm()
    if form.validate_on_submit():
        new_lecturer = Lecturer(
            name=form.name.data,
            email=form.email.data,
            dob=form.dob.data,
            password=generate_password_hash(form.password.data),
            profile_image_url=form.profile_picture.data,
            lecturer_id=form.lecturer_id.data
        )
        db.session.add(new_lecturer)
        db.session.commit()
        flash('Lecturer added successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_lecturers'))
    return render_template('admin/add_lecturer.html', form=form, user_type = 'admin')

# Admin delete lecturer route
@blueprint.route('/lecturers/delete/<int:lecturer_id>', methods=['POST'])
@login_required
def delete_lecturer(lecturer_id):
    lecturer = Lecturer.query.get_or_404(lecturer_id)
    db.session.delete(lecturer)
    db.session.commit()
    flash('Lecturer deleted successfully.', 'success')
    return redirect(url_for('admin_blueprint.view_lecturers'))

# Admin edit lecturer route
@blueprint.route('/lecturers/edit/<int:lecturer_id>', methods=['GET', 'POST'])
@login_required
def edit_lecturer(lecturer_id):
    lecturer = Lecturer.query.get_or_404(lecturer_id)
    form = LecturerForm(obj=lecturer)
    if form.validate_on_submit():
        form.populate_obj(lecturer)
        db.session.commit()
        flash('Lecturer updated successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_lecturers'))
    return render_template('admin/edit_lecturer.html', form=form, lecturer=lecturer, user_type = 'admin')

# Admin view all courses route
@blueprint.route('/courses')
@login_required
def view_courses():
    form = CourseForm()
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses, user_type = 'admin', form=form)

# Admin add course route
@blueprint.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        new_course = Course(
            name=form.name.data,
            code=form.code.data,
            lecturer=form.lecturer.data
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_courses'))
    return render_template('admin/add_course.html', form=form, user_type = 'admin')

# Admin delete course route
@blueprint.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Delete associated records from student_courses association table
    db.session.query(student_courses).filter_by(course_id=course_id).delete()
    
    # Delete associated records from lecturer_courses association table
    db.session.query(lecturer_courses).filter_by(course_id=course_id).delete()
    
    # Now delete the course itself
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('admin_blueprint.view_courses'))

# Admin edit course route
@blueprint.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Course updated successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_courses'))
    return render_template('admin/edit_course.html', form=form, course=course, user_type = 'admin')

# Admin view all attendance records route
@blueprint.route('/attendance-records')
@login_required
def view_attendance_records():
    form = SearchForm(request.form)
    records = AttendanceRecord.query.all()
    return render_template('admin/attendance_records.html', records=records, user_type='admin', form=form)

# Admin add attendance record route
@blueprint.route('/attendance-records/add', methods=['GET', 'POST'])
@login_required
def add_attendance_record():
    form = AttendanceRecordForm()
    if form.validate_on_submit():
        new_record = AttendanceRecord(
            student_id=form.student.data,
            course_id=form.course.data,
            timestamp=form.timestamp.data,
            status=form.status.data,
            lecturer_id=form.lecturer.data
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Attendance record added successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_attendance_records'))
    return render_template('admin/add_attendance_record.html', form=form, user_type='admin')

# Admin delete attendance record route
@blueprint.route('/attendance-records/delete/<int:record_id>', methods=['POST'])
@login_required
def delete_attendance_record(record_id):
    record = AttendanceRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash('Attendance record deleted successfully.', 'success')
    return redirect(url_for('admin_blueprint.view_attendance_records'))

# Admin edit attendance record route
@blueprint.route('/attendance-records/edit/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_attendance_record(record_id):
    record = AttendanceRecord.query.get_or_404(record_id)
    form = AttendanceRecordForm(obj=record)
    if form.validate_on_submit():
        form.populate_obj(record)
        db.session.commit()
        flash('Attendance record updated successfully.', 'success')
        return redirect(url_for('admin_blueprint.view_attendance_records'))
    return render_template('admin/edit_attendance_record.html', form=form, record=record, user_type='admin')

# Admin manage attendance route
@blueprint.route('/attendance', methods=['GET', 'POST'])
@login_required
def manage_attendance():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        date = form.date.data
        lecturer_id = form.lecturer.data
        student_id = form.student.data
        course_code = form.course.data

        attendance_records = AttendanceRecord.query.filter_by(timestamp=date)

        if lecturer_id:
            attendance_records = attendance_records.filter_by(lecturer_id=lecturer_id)
        if student_id:
            attendance_records = attendance_records.filter_by(student_id=student_id)
        if course_code:
            attendance_records = attendance_records.join(Course).filter_by(code=course_code)

        attendance_records = attendance_records.all()

        if attendance_records:
            flash('Attendance records found.', 'success')
        else:
            flash('No attendance records found.', 'warning')

        return render_template('admin/attendance_records.html', form=form, records=attendance_records, user_type='admin')

    return render_template('admin/attendance_records.html', form=form, user_type='admin')