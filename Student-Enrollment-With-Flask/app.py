from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text, true, ForeignKey, false
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user
from sqlalchemy.dialects.sqlite import json
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Update as needed
app.config['SECRET_KEY'] = 'hxjowf'  # random characters

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# class to hold different roles
class UserRoles:
    TEACHER = 'teacher'
    STUDENT = 'student'
    ADMIN = 'admin'


# database models for the user, classes, and class enrollments

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
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

    @validates('role')
    def validate_role(self, key, role):
        if role not in [UserRoles.TEACHER, UserRoles.STUDENT, UserRoles.ADMIN]:
            raise ValueError("Invalid role.")
        return role


class Classes(db.Model):
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(255))
    instructor_name = db.Column(db.String(255))
    instructor_id = db.Column(db.Integer, ForeignKey('user.user_id'))
    times_held = db.Column(db.String(300))
    capacity_limit = db.Column(db.Integer)


class ClassEnrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, ForeignKey('classes.class_id'), nullable=False)
    student_id = db.Column(db.Integer, ForeignKey('user.user_id'), nullable=False)
    grade = db.Column(db.Float(4), default=0.0)

    # Relationship to access class info directly from an enrollment instance
    class_info = db.relationship('Classes', backref='enrollments')


# flask-login
# reloads the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# default data
# has 4 students, 3 teachers, and 1 admin
# update: has 1 class with John Smith as teacher and 1 student Jim Doe
# jim doe is enrolled in math101
#############
# update: passwords now encrypted
# update 2: has more default data
# update: betty brown is enrolled into math101
################

# need to add error handling for existing students/admins/teachers/classes/classenrollments

def insert_default_data():
    new_student1 = User(name='Jim Doe', username='jimdoe', role='student')
    new_student1.set_password("password123")
    db.session.add(new_student1)

    new_student2 = User(name='Jose Santos', username='josesantos', role='student')
    new_student2.set_password("realpassword123")
    db.session.add(new_student2)

    new_student3 = User(name='Nancy Little', username='nancylittle', role='student')
    new_student3.set_password("opassword123")
    db.session.add(new_student3)

    new_student4 = User(name='Betty Brown', username='bettybrown2', role='student')
    new_student4.set_password("rpassword456")
    db.session.add(new_student4)

    teacher1 = User(name='Ammon Hepworth', username='ammonhepworth', role='teacher')
    teacher1.set_password("teacherPass12")
    db.session.add(teacher1)

    teacher2 = User(name='John Smith', username='johnsmith', role='teacher')
    teacher2.set_password("xyz123")
    db.session.add(teacher2)

    teacher3 = User(name='Susan Walker', username='susanwalker', role='teacher')
    teacher3.set_password("123xyz")
    db.session.add(teacher3)

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
        class1 = Classes(class_name='Math 101', instructor_name=instructor.name, instructor_id=instructor.user_id,
                         times_held='MWF 1:30-2:45PM', capacity_limit=3)
        db.session.add(class1)
        db.session.commit()
        print("class math101 successfully added")
    else:
        print("instructor not found")

    # enroll jim doe into math101
    if class1:
        student = User.query.filter_by(username='jimdoe').first()
        if student:
            class_enroll_jim_doe = ClassEnrollment(class_id=class1.class_id, student_id=student.user_id, grade=80.1)
            db.session.add(class_enroll_jim_doe)
            db.session.commit()
        print("successfully enrolled jimdoe into math101 for default data")

    # enroll betty brown into math101
    if class1:
        student = User.query.filter_by(username='bettybrown2').first()
        if student:
            class_enroll_betty_brown = ClassEnrollment(class_id=class1.class_id, student_id=student.user_id, grade=90.5)
            db.session.add(class_enroll_betty_brown)
            db.session.commit()
        print("successfully enrolled betty brown into math101 for default data")

    class2 = None

    ##class and class enrollment default data
    instructor = User.query.filter_by(username='ammonhepworth').first()
    if instructor:
        # Now that you have the correct instructor, proceed to create the class with the fetched instructor_id
        class2 = Classes(class_name='CSE 108', instructor_name=instructor.name, instructor_id=instructor.user_id,
                         times_held='Th 5-7PM', capacity_limit=2)
        db.session.add(class2)
        db.session.commit()
        print("class cse108 successfully added with ammon hepworth")
    else:
        print("instructor not found")

    # enroll jim doe into math101
    if class2:
        student = User.query.filter_by(username='jimdoe').first()
        if student:
            class_enroll_jim_doe = ClassEnrollment(class_id=class2.class_id, student_id=student.user_id, grade=80.1)
            db.session.add(class_enroll_jim_doe)
            db.session.commit()
        print("successfully enrolled jimdoe into cse108 for default data")

    # enroll betty brown into math101
    if class2:
        student = User.query.filter_by(username='josesantos').first()
        if student:
            class_enroll_jose = ClassEnrollment(class_id=class2.class_id, student_id=student.user_id, grade=90.5)
            db.session.add(class_enroll_jose)
            db.session.commit()
        print("successfully enrolled jose santos into cse108 for default data")


with app.app_context():
    db.drop_all()  # Delete the previous cache database
    db.create_all()
    insert_default_data()
    print("database successfully created")


# setup so default page is the login
@app.route('/')
def home():
    return render_template('login-teacher.html')


# routes for student_dashboard and teacher_dasboard

# UPDATE: is returning all 3 tables:
# users, classes, and classenrollments
# VIEWABLE ONLY
@app.route('/admin')
@login_required
def admin_dashboard():
    # check if user is an admin so they can view the data here
    if current_user.role != 'admin':
        flash('You do not have permission to view this page.', 'warning')
        return redirect(url_for('home'))  # Redirect to login page

    users_data = User.query.all()
    # Create a list of dictionaries for each user
    users_list = [
        {"user_id": user.user_id, "Name": user.name, "Username": user.username, "Password": user.password,
         "Role": user.role}
        for user in users_data
    ]

    # query and dictionary data for the classes
    classes_data = Classes.query.all()

    classes_list = [
        {"class_id": classes.class_id, "instructor_name": classes.instructor_name,
         "instructor_id": classes.instructor_id, "times_held": classes.times_held,
         "Capacity Limit": classes.capacity_limit}
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# view the classes a student is in already
@app.route('/student/dashboard')
# @login_required
def student_dashboard():
    default_user = User.query.filter_by(username="jimdoe").first()

    display_name = default_user.name
    # find the classes that the student is enrolled in
    classes_enrolled_in = ClassEnrollment.query.filter_by(student_id=default_user.user_id).all()

    class_info_list = [{
        "Class Name": enrollment.class_info.class_name,
        "Times held": enrollment.class_info.times_held,
        "Teacher": enrollment.class_info.instructor_name,
        "Students enrolled": len(enrollment.class_info.enrollments),
        "Capacity Limit": enrollment.class_info.capacity_limit
    } for enrollment in classes_enrolled_in]

    # put correct html file name here but student.html is placeholder
    return render_template('student.html', display_name=default_user.name, class_info_list=class_info_list)


#####below requires login functionality#######

# Access the name of the currently logged-in user so it can be displayed in top corner
    # display_name = current_user.name
    #
    # # make sure the user viewing this page is a student
    # if not current_user or current_user.role != 'student':
    #     # raise error if not student
    #     flash('Access denied. This page is for students only.', 'error')
    #     return redirect(url_for('login'))  # redirect to login page
    #
    # # find the classes that the student is enrolled in
    # classes_enrolled_in = ClassEnrollment.query.filter_by(student_id=current_user.user_id).all()
    #
    # class_info_list = [{
    #     "class_name": enrollment.class_info.class_name,
    #     "times_held": enrollment.class_info.times_held,
    #     "instructor_name": enrollment.class_info.instructor_name,
    #     "capacity_limit": enrollment.class_info.capacity_limit
    # } for enrollment in classes_enrolled_in]
    #
    # # put correct html file name here but student.html is placeholder
    # return render_template('student.html', display_name=current_user.name, class_info_list=class_info_list)

#######################

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    # Access the name of the currently logged-in user so it can be displayed in top corner
    display_name = current_user.name

    # make sure the user viewing this page is a student
    if not current_user or current_user.role != 'teacher':
        # raise error if not student
        flash('Access denied. This page is for teachers only.', 'error')
        return redirect(url_for('login'))  # redirect to login page

    # find the classes that the teacher is teaching
    classes_teaching = Classes.query.filter_by(instructor_id=current_user.user_id).all()
    class_info_list = [{
        "Class Name": class_taught.class_name,
        "Times held": class_taught.times_held,
        "Students enrolled": len(class_taught.enrollments),
        "Capacity Limit": class_taught.capacity_limit
    } for class_taught in classes_teaching]


# put correct html file name here but teacher.html is placeholder
    #python dictionary returned
    return render_template('teacher.html', display_name=current_user.name, class_info_list=class_info_list)
    # return display_name, classes_list


#####################
# function for login
# should work- awaiting frontend
########################
@app.route('/login')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # need these from front end
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # check roles and bring to correct page
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'student':  # NEEDS THE STUDENT VIEW
                return redirect(url_for('student_dashboard'))  # needs the correct html name

            elif user.role == 'teacher':  # NEEDS THE TEACHER VIEW
                return redirect(url_for('teacher_dashboard'))  # depends on html name
        else:
            # If authentication fails, reload the login page with an error
            flash('Invalid username or password.', 'error')
    # For GET requests or failed login attempts
    return render_template('login-teacher.html')


# Remove cache to prevent errors
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


if __name__ == '__main__':
    app.run()
