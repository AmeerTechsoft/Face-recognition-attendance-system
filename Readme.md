# Face Recognition Attendance System

This repository contains the codebase for a face recognition attendance system developed using Python and Flask.

## Introduction

The face recognition attendance system is designed to automate the process of taking attendance in educational institutions using facial recognition technology. It allows students to mark their attendance by capturing their faces through a webcam, which are then matched against a pre-trained model to verify their identity.

## Features

- Automatic face detection and recognition
- User authentication for students, lecturers, and administrators
- Course management functionality
- Attendance recording and tracking
- Responsive web interface for easy access on multiple devices

## Installation

1. Clone the repository:

'''
git clone https://github.com/AmeerTechsoft/face-recognition-attendance-system.git
'''

2. Install dependencies:

'''
cd face-recognition-attendance-system
pip install -r requirements.txt
'''


3. Set up the database:

'''
flask init db
flask migrate db
flask upgrade db




4. Run the application:

'''
flask run
'''


5. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Register as a student, lecturer, or administrator using the provided interface.
2. Log in with your credentials to access the respective functionalities.
3. For students, view available courses, mark attendance, and view attendance records.
4. For lecturers, manage courses and view attendance records of students.
5. For administrators, manage students, lecturers, courses, and attendance records.

## System Architecture

The face recognition attendance system follows a client-server architecture. The client-side interface is built using HTML, CSS, and JavaScript, while the server-side logic is implemented in Python using the Flask framework. The face recognition functionality is powered by the OpenCV and MediaPipe libraries, with trained models for face detection and recognition.

## Contributing

Contributions are welcome! Please feel free to submit bug reports, feature requests, or pull requests to help improve the face recognition attendance system.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.