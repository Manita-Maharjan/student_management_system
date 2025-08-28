# Student Management System

This is a backend system for managing student profiles and their academic data, developed using Django's Model–View–Template (MVT) architecture. It includes a simple frontend interface for CRUD (Create, Read, Update, Delete) operations on various entities, without using an API.

## 🌟 Features

* **Student Management:** CRUD functionality for student profiles, including first/last name, email, and date of birth.
* **Academic Data:** Models to manage Courses, Instructors, and student Enrollments with grades and scores.
* **Templating:** A simple, interactive frontend built with Django templates, HTML, CSS, JavaScript, and jQuery.
* **Search & Filtering:** Functionality to search for students and courses.

## 🚀 Setup and Installation

### 1. Prerequisites

Make sure you have Python and Git installed on your system.

### 2. Clone the Repository

Clone this project to your local machine and run the server using the following command:
```bash
git clone https://github.com/Manita-Maharjan/student_management_system.git
cd SMS
# Create a virtual environment
python -m venv venv
# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
# Install Dependency
pip install -r requirements.txt
# Database migration
python manage.py migrate
# Create Superuser
python manage.py createsuperuser
# Run the development Server
python manage.py runserver
