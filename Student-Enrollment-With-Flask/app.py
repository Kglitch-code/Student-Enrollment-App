from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import os, time
from sqlalchemy import text, true, ForeignKey, false
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user
from sqlalchemy.dialects.sqlite import json
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask_admin import Admin, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Update as needed
app.config['SECRET_KEY'] = 'hxjowf'  # random characters

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

admin = Admin(app, name='MyApp', template_mode='bootstrap3')


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

    def get_id(self):
        return str(self.user_id)


class Classes(db.Model):
    class_id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(255))
    instructor_name = db.Column(db.String(255))
    instructor_id = db.Column(db.Integer, ForeignKey('user.user_id'))
    times_held = db.Column(db.String(300))
    capacity_limit = db.Column(db.Integer)

    def get_id(self):
        return str(self.class_id)


class ClassEnrollment(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, ForeignKey('classes.class_id'), nullable=False)
    student_id = db.Column(db.Integer, ForeignKey('user.user_id'), nullable=False)
    grade = db.Column(db.Float(4), default=0.0)

    student = db.relationship('User', foreign_keys=[student_id], backref='enrollments')
    # Relationship to access class info directly from an enrollment instance
    class_info = db.relationship('Classes', backref='enrollments')

    def get_id(self):
        return str(self.enrollment_id)


class BaseModelView(ModelView):
    form_excluded_columns = []

    def __init__(self, model, *args, **kwargs):
        super(BaseModelView, self).__init__(model, *args, **kwargs)
        # exclude primary key column
        self.form_excluded_columns = [column.name for column in model.__table__.primary_key.columns]


# class views for each model to ignore primary key by passing the model view
class UserModelView(BaseModelView):
    form_columns = ['user_id', 'name', 'username', 'password', 'role']

    # Labels for the columns
    column_labels = {
        'user_id': 'User Id',
        'name': 'Name',
        'username': 'Username',
        'password': 'Password',
        'role': 'Role'
    }

    # Fields to display in the list view
    column_list = ['user_id', 'name', 'username', 'password', 'role']

    def __init__(self, model, session, **kwargs):
        super(UserModelView, self).__init__(model, session, **kwargs)
        self.static_folder = 'static'
        self.name = 'User'

    def on_model_change(self, form, model, is_created):
        # If the user is being created, `is_created` will be True.
        # hash password on creation
        if is_created:
            model.password = generate_password_hash(form.password.data)
        super(UserModelView, self).on_model_change(form, model, is_created)



class ClassesModelView(BaseModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True

    # Fields to display in the form
    form_columns = ['class_name', 'instructor_name', 'instructor_id', 'times_held', 'capacity_limit']

    # Labels for the columns
    column_labels = {
        'class_name': 'Class Name',
        'instructor_name': 'Instructor',
        'instructor_id': 'Instructor ID',
        'times_held': 'Times Held',
        'capacity_limit': 'Capacity Limit'
    }

    # Fields to display in the list view
    column_list = ['class_name', 'instructor_name', 'instructor_id', 'times_held', 'capacity_limit']

    def __init__(self, model, session, **kwargs):
        super(ClassesModelView, self).__init__(model, session, **kwargs)
        self.static_folder = 'static'
        self.name = 'Classes'

    def after_model_change(self, form, model, is_created):
        super(ClassesModelView, self).after_model_change(form, model, is_created)
        if is_created:
            print(f"New class added: {model.class_name} by instructor {model.instructor_name}")
        else:
            print(f"Class updated: {model.class_name}")


class ClassEnrollmentModelView(BaseModelView):
    column_list = ('enrollment_id', 'class_id', 'class_info.class_name', 'student.name', 'student_id', 'grade')
    column_labels = {
        'class_id': 'Class ID',
        'class_info.class_name': 'Class Name',
        'student.name': 'Student Name',
        'student_id': 'Student ID',
        'grade': 'Grade'
    }

    def __init__(self, model, session, **kwargs):
        super(ClassEnrollmentModelView, self).__init__(model, session, **kwargs)
        self.static_folder = 'static'
        # self.endpoint = 'admin.index'
        self.name = 'Class Enrollment'


# flask views
admin.add_view(UserModelView(User, db.session))
admin.add_view(ClassesModelView(Classes, db.session))
admin.add_view(ClassEnrollmentModelView(ClassEnrollment, db.session))


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
            existing_enrollment = ClassEnrollment.query.filter_by(class_id=class1.class_id, student_id=student.user_id).first()
            if not existing_enrollment:
                try:
                    class_enroll_jim_doe = ClassEnrollment(class_id=class1.class_id, student_id=student.user_id)
                    db.session.add(class_enroll_jim_doe)
                    db.session.commit()
                    print("Successfully enrolled Jim Doe into Math 101.", "success")
                except Exception as e:
                    db.session.rollback()
                    print("An error occurred while enrolling Jim Doe into Math 101.", "error")
            else:
                print("Jim Doe is already enrolled in Math 101.", "info")
        else:
            print("Student Jim Doe not found.", "error")
    # enroll betty brown into math101
    if class1:
        student = User.query.filter_by(username='bettybrown2').first()
        if student:
            existing_enrollment = ClassEnrollment.query.filter_by(class_id=class1.class_id, student_id=student.user_id).first()
            if not existing_enrollment:
                try:
                    class_enroll_jim_doe = ClassEnrollment(class_id=class1.class_id, student_id=student.user_id)
                    db.session.add(class_enroll_jim_doe)
                    db.session.commit()
                    print("Successfully enrolled Betty Brown into Math 101.", "success")
                except Exception as e:
                    db.session.rollback()
                    print("An error occurred while enrolling Betty Brown into Math 101.", "error")
            else:
                print("Betty Brown is already enrolled in Math 101.", "info")
        else:
            print("Student Betty Brown not found.", "error")

    class2 = None

    ##class and class enrollment default data
    instructor = User.query.filter_by(username='ammonhepworth').first()
    if instructor:
        # Now that you have the correct instructor, proceed to create the class with the fetched instructor_id
        class2 = Classes(class_name='CSE 108', instructor_name=instructor.name, instructor_id=instructor.user_id,
                         times_held='TR 5-7PM', capacity_limit=2)
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

    class3= None

    ##class and class enrollment default data
    instructor = User.query.filter_by(username='johnsmith').first()
    if instructor:
        # Now that you have the correct instructor, proceed to create the class with the fetched instructor_id
        class3 = Classes(class_name='Math 32', instructor_name=instructor.name, instructor_id=instructor.user_id,
                         times_held='MW 5-7PM', capacity_limit=2)
        db.session.add(class3)
        db.session.commit()
        print("class math 32 succesfully added with johnsmith instructor")
    else:
        print("instructor not found")

    if class3:
        student = User.query.filter_by(username='nancylittle').first()
        if student:
            class_enroll_nancy = ClassEnrollment(class_id=class3.class_id, student_id=student.user_id, grade=90.5)
            db.session.add(class_enroll_nancy)
            db.session.commit()
        print("successfully enrolled nancy little into math32 for default data")

# create database
with app.app_context():
    db.drop_all()  # Delete the previous cache database
    db.create_all()
    insert_default_data()
    print("database successfully created")


# setup so default page is the login
@app.route('/')
def home():
    return render_template('login-teacher.html')


# UPDATE: is returning all 3 tables:
# users, classes, and classenrollments
# VIEWABLE ONLY
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # check if user is an admin so they can view the data here
    if current_user.role != 'admin':
        print('You do not have permission to view this page.', 'warning')
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

    users_list = json.dumps(users_list)
    classes_list = json.dumps(classes_list)
    class_enroll_list = json.dumps(class_enroll_list)
    return render_template('admin.html', users_data=users_list, classes_data=classes_list,
                           class_enroll_data=class_enroll_list)  # send data, display page


# sign out button
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# view the classes a student is already enrolled in
@app.route('/student/dashboard')
@login_required
def student_dashboard():

    #current user logged in display their name
    display_name = current_user.name

    # make sure the current user is a student
    if not current_user or current_user.role != 'student':
        # raise error if not student
        print('Access denied. This page is for students only.', 'error')
        return redirect(url_for('login'))  # redirect to login page

    # find the classes that the student is enrolled in
    classes_enrolled_in = ClassEnrollment.query.filter_by(student_id=current_user.user_id).all()

    class_info_list = [{
        "Class Name": enrollment.class_info.class_name,
        "Times held": enrollment.class_info.times_held,
        "Teacher": enrollment.class_info.instructor_name,
        "Students enrolled": len(enrollment.class_info.enrollments),
        "Capacity Limit": enrollment.class_info.capacity_limit
    } for enrollment in classes_enrolled_in]

    class_info_list = json.dumps(class_info_list)
    # put correct html file name here but student.html is placeholder
    return render_template('student.html', display_name=current_user.name, class_info_list=class_info_list)


# student add/remove classes
@app.route('/student/dashboard/all-classes', methods=['GET', 'POST'])
@login_required
def change_classes():
    # display current user name in corner
    display_name = current_user.name

    # make sure user is a student
    if not current_user or current_user.role != 'student':
        # raise error if not student
        print('Access denied. This page is for students only.', 'error')
        return redirect(url_for('login'))  # redirect to login page

    # find all classes and display the info associated with them
    all_classes = Classes.query.all()

    class_info_list = [{
        "Class Name": classes_available.class_name,
        "Teacher Name": classes_available.instructor_name,
        "Times held": classes_available.times_held,
        "Students enrolled": len(classes_available.enrollments),
        "Capacity Limit": classes_available.capacity_limit
    } for classes_available in all_classes]

    # same format as student courses so the table stays insertion-order
    class_info_list = json.dumps(class_info_list)

    class_IDs = [{
        "ID": classes_available.class_id,
    } for classes_available in all_classes]
    
    class_IDs = json.dumps(class_IDs)

    if request.method == 'POST':
        data = request.json
        # add and remove classes depending on action
        class_id = data.get('class_id')
        option = data.get('option')  # action from front end will be add or delete
        print(class_id)
        print(option)
        # add the class
        if option == 'add':
            # Check if the class exists and capacity allows for more enrollments
            class_to_enroll = Classes.query.get(class_id)
            if class_to_enroll and len(class_to_enroll.enrollments) < class_to_enroll.capacity_limit:
                #check if student already enrolled in class
                if not ClassEnrollment.query.filter_by(class_id=class_id, student_id=current_user.user_id).first():
                    new_class_enroll = ClassEnrollment(class_id=class_id, student_id=current_user.user_id, grade=0.0)
                    db.session.add(new_class_enroll)
                    db.session.commit()
                    print("Successfully added new class", 'success')
                else:
                    print("Student already enrolled in class", 'info')
            else:
                print("Class is at full capacity", 'error')

        # delete the class
        elif option == 'delete':
            delete_class = ClassEnrollment.query.filter_by(class_id=class_id, student_id=current_user.user_id).first()
            # delete_class = ClassEnrollment.query.filter_by(class_id=class_id, student_id=current_user.user_id).first()
            # delete the class if the student is in it
            if delete_class:
                db.session.delete(delete_class)
                db.session.commit()
                print("successfully unenrolled in class")
            else:
                print("student not enrolled in class- unenrollment unavailable")

    # classes.html is placeholder
    return render_template('student-edit-courses.html', display_name=current_user.name, class_info_list=class_info_list, class_IDs=class_IDs)


# teacher dashboard with default data
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    # Access the name of the currently logged-in user so it can be displayed in top corner
    display_name = current_user.name

    # make sure the user viewing this page is a student
    if not current_user or current_user.role != 'teacher':
        # raise error if not student
        print('Access denied. This page is for teachers only.', 'error')
        return redirect(url_for('login'))  # redirect to login page

    # find the classes that the teacher is teaching
    classes_teaching = Classes.query.filter_by(instructor_id=current_user.user_id).all()
    # classes_teaching = Classes.query.filter_by(instructor_id=default_user.user_id).all()
    class_info_list = [{
        "Class Name": class_taught.class_name,
        "Times held": class_taught.times_held,
        "Students enrolled": len(class_taught.enrollments),
        "Capacity Limit": class_taught.capacity_limit
    } for class_taught in classes_teaching]

    # same format as student courses
    class_info_list = json.dumps(class_info_list)

    class_IDs = [{
        "ID": class_taught.class_id,
    } for class_taught in classes_teaching]

    class_IDs = json.dumps(class_IDs)

    return render_template('teacher.html', display_name=current_user.name, class_info_list=class_info_list,
                           class_IDs=class_IDs)


# edit grades for the selected class
@app.route('/teacher/dashboard/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_grades(class_id):
    # Access the name of the currently logged-in user so it can be displayed in top corner
    display_name = current_user.name

    # make sure the user viewing this page is a student
    if not current_user or current_user.role != 'teacher':
        # raise error if not student
        print('Access denied. This page is for teachers only.', 'error')
        return redirect(url_for('login'))  # redirect to login page

    # edit the grade
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        new_grade = request.form.get('new_grade')

        # find the student's grade by the class_id and student_id
        enrollment_record = ClassEnrollment.query.filter_by(class_id=class_id, student_id=student_id).first()

        if enrollment_record:
            enrollment_record.grade = new_grade
            db.session.commit()
            print('Grade updated successfully.', 'success')
        else:
            print('Enrollment record not found.', 'error')
    # get the class id from the route
    class_to_edit = Classes.query.get_or_404(class_id)

    # get the students names for the students in the class
    enrollments = db.session.query(User.name, ClassEnrollment.student_id, ClassEnrollment.grade) \
        .join(User, ClassEnrollment.student_id == User.user_id) \
        .filter(ClassEnrollment.class_id == class_id) \
        .all()

    grade_list = [{
        "Student Name": enrollment[0],
        "Student Id": enrollment[1],
        "Grade": enrollment[2]
    } for enrollment in enrollments]

    # # debugging
    # for index, item in enumerate(grade_list):
    #     if not isinstance(item, dict):
    #         print(f"Item at index {index} is not a dictionary. Type: {type(item)}")
    #         continue  # Skip to the next item if this one isn't a dictionary
    #
    #     for key, value in item.items():
    #         if not isinstance(value, (str, int, float, list, dict, bool, type(None))):
    #             print(f"Non-serializable type found at index {index}, key '{key}': {type(value)}")
    #         else:
    #             print(f"Item at index {index}, key '{key}' is of serializable type: {type(value)}")

    grade_list = json.dumps(grade_list)


    # assuming grades html
    return render_template('grades.html', display_name=current_user.name, grade_list=grade_list, class_id=class_id)


# function for login
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
                return redirect(url_for('admin.index'))
            elif user.role == 'student':  # NEEDS THE STUDENT VIEW
                return redirect(url_for('student_dashboard'))  # needs the correct html name

            elif user.role == 'teacher':  # NEEDS THE TEACHER VIEW
                return redirect(url_for('teacher_dashboard'))  # depends on html name
        else:
            # If authentication fails, reload the login page with an error
            print('Invalid username or password.', 'error')
    # For GET requests or failed login attempts
    return render_template('login-teacher.html')


#cache buster
@app.context_processor
def inject_cache_buster():
    def cache_buster():
        return int(time.time())

    return dict(cache_buster=cache_buster)


# Remove cache to prevent errors - additional method
@app.after_request
def add_cache_control_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.run()
