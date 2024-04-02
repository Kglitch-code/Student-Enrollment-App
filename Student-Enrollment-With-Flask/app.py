from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text, true, ForeignKey, false
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user

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

    def check_password(self, password):
        return self.password == password

    #################
    #add password encryption here
    ######################

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
#############
#encrypt these passwords too
################
def insert_default_data():
    new_student1 = User(name='John Doe', username='johndoe', password='password123', role='student')
    db.session.add(new_student1)

    new_student2 = User(name='Jose Santos', username='josesantos', password='rEAlpAsswOrd123', role='student')
    db.session.add(new_student2)

    teacher1 = User(name='Ammon Hepworth', username='ammonhepworth', password='teacherPass12', role='teacher')
    db.session.add(teacher1)

    teacher2 = User(name='John Smith', username='johnsmith', password='xyz123', role='teacher')
    db.session.add(teacher2)

    admin1 = User(name='admin1', username='admin1', password='supersecretpassword123', role='admin')
    db.session.add(admin1)

    # commit all the new users
    db.session.commit()
    print("added default data successful")


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
#function for login
#needs to be post but currently throwing errors- possibly because not receiving info ?
########################
#@app.route('/login')
#@app.route('/login', METHOD='POST')

#DOESNT LIKE POST METHOD- will check
#def login_page():
  #cannot render_template up here
    #username = request.form['username']
    #password = request.form['password']
    #user = User.query.filter_by(username=username).first()
    #if user and user.check_password(password):
     #   login_user(user)
        #check roles and bring to correct page
        #if user.role == 'admin':
       #     next_page = url_for('admin_dashboard') #depends on html name
       # elif user.role == 'student':
        #    next_page = url_for('student_dashboard') #depends on html name
       # elif user.role == 'teacher':
        #    next_page = url_for('teacher_dashboard') #depends on html name
   #return true #DEFAULT DO NOT USE
    #return redirect(next_page)
   # return render_template('login-teacher.html')

#log a user out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
# route to view all users
# currently used for testing but can be used for the admin role
# @login_required #login required isnt working/not checking
# possibly because login hasny been implemented entirely
@app.route('/view_users')
def view_users():
    # check if user is an admin so they can view the data here
    #  if current_user.role != 'admin':
    #   flash('You do not have permission to view this page.', 'warning')
    #  return redirect(url_for('some_other_route'))  # Redirect to another page

    users = User.query.all()
    user_data = []
    for user in users:
        user_data.append(f"ID: {user.user_id}, Name: {user.name}, Username: {user.username}, Role: {user.role}")
    return '<br>'.join(user_data)  # Display as simple HTML or return as JSON


# app.route('/login', METHODS= 'POST')
# def login():


if __name__ == '__main__':
    app.run()
