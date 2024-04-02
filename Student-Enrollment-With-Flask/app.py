from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
db = SQLAlchemy(app)


# Create the database
# need to insert default data
def init_db():
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            sql_file_path = os.path.join(os.path.dirname(__file__), 'database.sql')
            with open(sql_file_path, 'r') as f:
                sql_commands = f.read().split(';')  # Split the file into individual commands
                for command in filter(None, sql_commands):  # Filter out empty commands
                    # Execute each command
                    db.session.execute(text(command))
                # Commit changes
                db.session.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print("An error occurred while initializing the database:", e)


#need to call database creation here
init_db()

@app.route('/')
def home():
    return render_template('login-teacher.html')


# need a page for this or login-teacher can work for all login-types
# @app.route('/login-page')
# def login_teacher():
# return render_template('login-teacher.html')


if __name__ == '__main__':
    #app.run(debug=True)
    app.run()
