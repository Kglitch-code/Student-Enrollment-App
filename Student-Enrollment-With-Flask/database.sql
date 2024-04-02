CREATE TABLE IF NOT EXISTS sessions (
      session_id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INT NOT NULL,
      login_time TIMESTAMP NOT NULL,
      logout_time TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS users (
       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
       name VARCHAR(255),
       username VARCHAR(255) UNIQUE NOT NULL,
       password TEXT NOT NULL,
       role TEXT CHECK(role IN ('student', 'teacher', 'admin'))
);

CREATE TABLE IF NOT EXISTS classes (
    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name VARCHAR(255),
    instructor_name VARCHAR(255),  -- Consider linking to the `users` table instead
    instructor_id INT NOT NULL,
    times_held TEXT,
    capacity_limit INT,
    FOREIGN KEY (instructor_id) REFERENCES users(user_id)
);

--table to connect the students, classes, and teachers
CREATE TABLE IF NOT EXISTS class_enrollments (
   enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
   class_id INT NOT NULL,
   student_id INT NOT NULL,  -- Use `user_id` from the `users` table where `role` = 'student'
   grade FLOAT(4), REAL NOT NULL DEFAULT 0.0, -- grades are numbers
   FOREIGN KEY (class_id) REFERENCES classes(class_id),
   FOREIGN KEY (student_id) REFERENCES users(user_id)
);


