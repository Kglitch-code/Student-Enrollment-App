from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text, true, ForeignKey, false
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user
from sqlalchemy.dialects.sqlite import json
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Update as needed
app.config['SECRET_KEY'] = 'hxjowf'  # random characters

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# database models for the user, classes, and class enrollments

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=true)
    name = db.Column(db.String(255))
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)

    # password hashing
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # checking the hashed password in the db
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Classes(db.Model):
    class_id = db.Column(db.Integer, primary_key=true)
    class_name = db.Column(db.String(255))
    instructor_name = db.Column(db.String(255))
    instructor_id = db.Column(db.Integer, ForeignKey('user.user_id'))
    times_held = db.Column(db.String(300))
    capacity_limit = db.Column(db.Integer)


class ClassEnrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=true)
    class_id = db.Column(db.Integer, ForeignKey('classes.class_id'), nullable=false)
    student_id = db.Column(db.Integer, ForeignKey('user.user_id'), nullable=false)
    grade = db.Column(db.Float(4), default=0.0)


# flask-login
# reloads the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# default data
# has 2 students, 2 teachers, and 1 admin so far
# update: has 1 class with John Smith as teacher and 1 student Jim Doe
#############
# update: passwords now encrypted
################
def insert_default_data():
    new_student1 = User(name='Jim Doe', username='jimdoe', role='student')
    new_student1.set_password("password123")
    db.session.add(new_student1)

    new_student2 = User(name='Jose Santos', username='josesantos', role='student')
    new_student2.set_password("realpassword123")
    db.session.add(new_student2)

    teacher1 = User(name='Ammon Hepworth', username='ammonhepworth', role='teacher')
    teacher1.set_password("teacherPass12")
    db.session.add(teacher1)

    teacher2 = User(name='John Smith', username='johnsmith', role='teacher')
    teacher2.set_password("xyz123")
    db.session.add(teacher2)

    admin1 = User(name='admin1', username='admin1', role='admin')
    admin1.set_password("supersecretpassword123")
    db.session.add(admin1)

    # commit all the new users
    db.session.commit()
    print("user default data successful")

    class1 = None

    ##class and class enrollment default data
    instructor = User.query.filter_by(username='johnsmith').first()
    if instructor:
    # Now that you have the correct instructor, proceed to create the class with the fetched instructor_id
        class1 = Classes(class_name='Math 101', instructor_name=instructor.name, instructor_id=instructor.user_id, times_held='MWF 1:30-2:45PM', capacity_limit=30)
        db.session.add(class1)
        db.session.commit()
        print("class successfully added")
    else:
        print("instructor not found")


    if class1:
        student = User.query.filter_by(username='jimdoe').first()
        if student:
            class_enroll_jim_doe = ClassEnrollment(class_id= class1.class_id, student_id = student.user_id, grade = 80.1)
            db.session.add(class_enroll_jim_doe)
            db.session.commit()
    print("successfully enrolled jimdoe for default data")


with app.app_context():
    db.drop_all()  # Delete the previous cache database
    db.create_all()
    insert_default_data()
    print("database successfully created")


# setup so default page is the login
@app.route('/')
def home():
    return render_template('login-teacher.html')


#####################
# function for login
# needs to be post but currently throwing errors- possibly because not receiving info ?
########################
# @app.route('/login')
# @app.route('/login', METHOD='POST')

# DOESNT LIKE POST METHOD- will check
# def login_page():
# cannot render_template up here
# username = request.form['username']
# password = request.form['password']
# user = User.query.filter_by(username=username).first()
# if user and user.check_password(password):
#   login_user(user)
# check roles and bring to correct page
# if user.role == 'admin':
#     next_page = url_for('admin_dashboard') #depends on html name
# elif user.role == 'student':
#    next_page = url_for('student_dashboard') #depends on html name
# elif user.role == 'teacher':
#    next_page = url_for('teacher_dashboard') #depends on html name
# return true #DEFAULT DO NOT USE
# return redirect(next_page)
# return render_template('login-teacher.html')

# log a user out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# route to view all users
# currently used for testing but can be used for the admin role
# @login_required #login required isnt working/not checking
# possibly because login hasny been implemented entirely


# UPDATE: is returning all 3 tables:
# users, classes, and classenrollments
# login_required
@app.route('/admin', methods=['GET'])
def view_users():
    # check if user is an admin so they can view the data here
    # if current_user.role != 'admin':
    #   flash('You do not have permission to view this page.', 'warning')
    #  return redirect(url_for('some_other_route'))  # Redirect to another page

    users_data = User.query.all()
    # Create a list of dictionaries for each user
    users_list = [
        {"user_id": user.user_id, "name": user.name, "username": user.username, "password": user.password,
         "role": user.role}
        for user in users_data
    ]

    # query and dictionary data for the classes
    classes_data = Classes.query.all()

    classes_list = [
        {"class_id": classes.class_id, "instructor_name": classes.instructor_name,
         "instructor_id": classes.instructor_id, "times_held": classes.times_held,
         "capacity_limit": classes.capacity_limit}
        for classes in classes_data
    ]

    # query and dictionary data for the class enrollments
    class_enroll_data = ClassEnrollment.query.all()

    class_enroll_list = [
        {"enrollment_id": classEnrollments.enrollment_id, "class_id": classEnrollments.class_id,
         "student_id": classEnrollments.student_id, "grade": classEnrollments.grade
         }

        for classEnrollments in class_enroll_data
    ]

    return render_template('admin.html', users_data=users_list, classes_data=classes_list,
                           class_enroll_data=class_enroll_list)  # send data, display page

    # comment the above return out and comment the below in if you want json
    ######LINE TO JSONIFY THE DATA########
    #
    # users_json = json.dumps(users_list)
    # return render_template('admin.html', users_data=users_list, users_json=users_json)
    #########################


# app.route('/login', METHODS= 'POST')
# def login():


# Remove cache to prevent errors
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run()
