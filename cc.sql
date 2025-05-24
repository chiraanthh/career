DROP DATABASE IF EXISTS cc;
CREATE DATABASE cc;
USE cc;

-- Counsellors table with authentication
CREATE TABLE counsellors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    specialization VARCHAR(100),
    qualification TEXT,
    years_of_experience INT,
    bio TEXT,
    availability_status BOOLEAN,
    rating DECIMAL(3, 2),
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);

-- Student table with authentication
CREATE TABLE student (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    phone VARCHAR(20),
    dob DATE,
    address TEXT,
    education_level VARCHAR(100),
    interests TEXT,
    counsellor_id INT,
    course VARCHAR(100),
    quiz_result VARCHAR(100) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id) ON DELETE SET NULL
);

-- Administrator table
CREATE TABLE administrators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    department VARCHAR(100),
    role_description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL
);

-- Grievances
CREATE TABLE grievances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('Pending', 'In Progress', 'Resolved') DEFAULT 'Pending',
    response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

-- Counsellor assignment logs
CREATE TABLE counsellor_assignment_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    old_counsellor_id INT,
    new_counsellor_id INT NOT NULL,
    reason TEXT,
    assigned_by_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (old_counsellor_id) REFERENCES counsellors(id) ON DELETE SET NULL,
    FOREIGN KEY (new_counsellor_id) REFERENCES counsellors(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_id) REFERENCES administrators(id)
);

-- Appointment requests
CREATE TABLE appointment_requests (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER NOT NULL,
    counsellor_id INTEGER NOT NULL,
    appointment_type VARCHAR(100) NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time TIME NOT NULL,
    mode VARCHAR(10) NOT NULL CHECK (mode IN ('online', 'offline', 'phone')),
    notes TEXT,
    status VARCHAR(10) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id) ON DELETE CASCADE
);

-- Appointments
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    counsellor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
    mode ENUM('online', 'offline', 'phone') NOT NULL,
    location VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id) ON DELETE CASCADE
);

-- Counselling sessions
CREATE TABLE counselling_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT,
    notes TEXT,
    recommendations TEXT,
    resources TEXT,
    follow_up_date DATE,
    session_duration INT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);

-- Feedback
CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    student_id INT,
    counsellor_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES counselling_sessions(session_id),
    FOREIGN KEY (student_id) REFERENCES student(id),
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id)
);

-- Counsellor schedules
CREATE TABLE counsellor_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    counsellor_id INT,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    start_time TIME,
    end_time TIME,
    is_recurring BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id) ON DELETE CASCADE
);

-- Career resources
CREATE TABLE career_resources (
    resource_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resource_type ENUM('document', 'video', 'link', 'other') NOT NULL,
    url VARCHAR(255),
    file_path VARCHAR(255),
    added_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_public BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (added_by) REFERENCES administrators(id)
);

-- Student documents
CREATE TABLE student_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    document_type ENUM('transcript', 'resume', 'certificate', 'other') NOT NULL,
    file_type VARCHAR(10) NOT NULL DEFAULT 'other',
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

-- Notifications
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_status BOOLEAN DEFAULT FALSE,
    notification_type ENUM('general', 'appointment', 'resource', 'payment', 'grievance', 'appointment_request') NOT NULL,
    related_entity_id INT,
    FOREIGN KEY (user_id) REFERENCES student(id) ON DELETE CASCADE
);

-- Messages
CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    recipient_id INT,
    message_text TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sender_id) REFERENCES student(id),
    FOREIGN KEY (recipient_id) REFERENCES student(id)
);

-- Career goals
CREATE TABLE career_goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    title VARCHAR(255),
    description TEXT,
    start_date DATE,
    target_date DATE,
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started',
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

-- Student resource access
CREATE TABLE student_resource_access (
    access_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    resource_id INT,
    access_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES career_resources(resource_id) ON DELETE CASCADE
);

-- Goal milestones
CREATE TABLE goal_milestones (
    milestone_id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT,
    milestone_title VARCHAR(255),
    due_date DATE,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    FOREIGN KEY (goal_id) REFERENCES career_goals(goal_id) ON DELETE CASCADE
);

-- Events
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type ENUM('webinar', 'workshop', 'qna', 'seminar') NOT NULL,
    counsellor_id INT,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    location VARCHAR(255),
    meeting_link VARCHAR(255),
    capacity INT,
    is_online BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (counsellor_id) REFERENCES counsellors(id)
);

-- Event registrations
CREATE TABLE event_registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    student_id INT,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reminder_sent BOOLEAN DEFAULT FALSE,
    attendance_status ENUM('registered', 'attended', 'missed') DEFAULT 'registered',
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

-- Tasks
CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE,
    priority VARCHAR(20) NOT NULL,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id)
);

-- Sample data: counsellors
INSERT INTO counsellors (
    first_name, last_name, email, password_hash, specialization, qualification,
    years_of_experience, bio, availability_status, rating, date_registered
) VALUES
('John', 'Doe', 'c1@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Technology', 'MSc Computer Science', 10, 'Experienced technology counsellor.', TRUE, 4.5, NOW()),
('Jane', 'Smith', 'c2@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Healthcare', 'MD Medicine', 8, 'Healthcare career counsellor.', TRUE, 4.6, NOW()),
('Michael', 'Brown', 'c3@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Business', 'MBA Finance', 12, 'Business and finance counsellor.', TRUE, 4.9, NOW()),
('Aisha', 'Patel', 'c4@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Engineering', 'BTech Mechanical Engineering', 7, 'Engineering career advisor.', TRUE, 4.7, NOW()),
('Padmavathi', 'Devarakonda', 'c5@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Arts', 'MA Fine Arts', 15, 'Arts and creative careers expert.', TRUE, 4.8, NOW()),
('Ahmed', 'Khan', 'c6@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Science', 'PhD Physics', 11, 'Science and research specialist.', TRUE, 4.8, NOW()),
('Rachel', 'Lee', 'c7@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Education', 'M.Ed.', 9, 'Education and teaching counsellor.', TRUE, 4.4, NOW()),
('Bharati', 'Trivedi', 'c8@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Law', 'LLM Law', 20, 'Legal careers and law expert.', TRUE, 4.7, NOW());


-- Sample data: administrators
INSERT INTO administrators (
    email, password_hash, first_name, last_name, department, role_description, is_active, date_registered
) VALUES
('admin@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Admin', 'User', 'IT', 'Superuser for the system', TRUE, NOW()),
('manager@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Manager', 'Smith', 'Operations', 'Operations manager', TRUE, NOW());

-- Sample data: students
INSERT INTO student (
    email, password_hash, first_name, last_name, phone, dob, address, education_level,
    interests, counsellor_id, course, quiz_result, is_active, date_registered
) VALUES
('student1@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Alice', 'Student', '9876543210', '2004-08-15', '123 Main St', 'High School', 'Science, Robotics', 1, 'BSc Physics', 'A', TRUE, NOW()),
('student2@example.com', 'pbkdf2:sha256:600000$f6Mv5oQIZnEFru6r$d2475f0b4b9707a14301c3c58a3ace3fdb357eb508a4bd66ea164e0988a19c81', 'Bob', 'Student', '9123456780', '2003-12-01', '456 Park Ave', 'Undergraduate', 'Business, Finance', 2, 'BBA', 'B', TRUE, NOW());

-- Sample data: grievances
INSERT INTO grievances (student_id, subject, description, status, response)
VALUES
(1, 'Delay in appointment', 'My appointment was delayed by 30 minutes.', 'Pending', NULL),
(2, 'Resource access issue', 'Unable to download career guide.', 'In Progress', 'We are looking into it.');

-- Sample data: counsellor_assignment_logs
INSERT INTO counsellor_assignment_logs (student_id, old_counsellor_id, new_counsellor_id, reason, assigned_by_id)
VALUES
(1, NULL, 1, 'Initial assignment', 1),
(2, 1, 2, 'Requested change by student', 2);

-- Sample data: appointment_requests
INSERT INTO appointment_requests (student_id, counsellor_id, appointment_type, preferred_date, preferred_time, mode, notes, status)
VALUES
(1, 1, 'Career Guidance', '2025-05-25', '10:00:00', 'online', 'Need advice on course selection.', 'pending'),
(2, 2, 'Personal Counseling', '2025-05-26', '14:30:00', 'offline', 'Discuss stress management.', 'approved');

-- Sample data: appointments
INSERT INTO appointments (student_id, counsellor_id, appointment_date, start_time, end_time, status, mode, location, payment_status)
VALUES
(1, 1, '2025-05-25', '10:00:00', '10:30:00', 'scheduled', 'online', NULL, 'not_required'),
(2, 2, '2025-05-26', '14:30:00', '15:00:00', 'scheduled', 'offline', 'Room 101', 'pending');

-- Sample data: counselling_sessions
INSERT INTO counselling_sessions (appointment_id, notes, recommendations, resources, follow_up_date, session_duration)
VALUES
(1, 'Discussed career options.', 'Explore STEM fields.', 'link1,doc2', '2025-06-01', 30),
(2, 'Talked about stress management.', 'Practice mindfulness.', 'video3', '2025-06-05', 30);

-- Sample data: feedback
INSERT INTO feedback (session_id, student_id, counsellor_id, rating, comments)
VALUES
(1, 1, 1, 5, 'Very helpful session.'),
(2, 2, 2, 4, 'Good advice, thank you.');

-- Sample data: counsellor_schedules
INSERT INTO counsellor_schedules (counsellor_id, day_of_week, start_time, end_time, is_recurring)
VALUES
(1, 'Monday', '09:00:00', '12:00:00', TRUE),
(2, 'Tuesday', '13:00:00', '16:00:00', TRUE);

-- Sample data: career_resources
INSERT INTO career_resources (title, description, resource_type, url, file_path, added_by)
VALUES
('Resume Writing Guide', 'Comprehensive guide to resume writing.', 'document', NULL, '/files/resume_guide.pdf', 1),
('Career in Data Science', 'Introductory video on data science careers.', 'video', 'https://youtube.com/datascience', NULL, 2);

-- Sample data: notifications
INSERT INTO notifications (user_id, message, notification_type, related_entity_id)
VALUES
(1, 'Your appointment is scheduled for 25 May.', 'appointment', 1),
(2, 'New career resource added: Resume Writing Guide.', 'resource', 1);

-- Sample data: messages
INSERT INTO messages (sender_id, recipient_id, message_text, is_read)
VALUES
(1, 2, 'Hi Bob, have you checked the new resource?', FALSE),
(2, 1, 'Yes, it was very helpful. Thanks!', TRUE);

-- Sample data: career_goals
INSERT INTO career_goals (student_id, title, description, start_date, target_date, status)
VALUES
(1, 'Get Internship', 'Secure a summer internship in IT.', '2025-05-01', '2025-07-01', 'in_progress'),
(2, 'Complete Certification', 'Finish finance certification course.', '2025-05-10', '2025-08-15', 'not_started');

-- Sample data: student_resource_access
INSERT INTO student_resource_access (student_id, resource_id)
VALUES
(1, 1),
(2, 2);

-- Sample data: goal_milestones
INSERT INTO goal_milestones (goal_id, milestone_title, due_date, status)
VALUES
(1, 'Apply to companies', '2025-06-01', 'pending'),
(2, 'Complete course modules', '2025-07-15', 'pending');

-- Sample data: events
INSERT INTO events (title, description, event_type, counsellor_id, event_date, start_time, end_time, location, meeting_link, capacity, is_online)
VALUES
('Webinar: Future Careers', 'A webinar on emerging career trends.', 'webinar', 1, '2025-06-10', '11:00:00', '12:00:00', NULL, 'https://meet.link/webinar', 100, TRUE),
('Workshop: Resume Building', 'Hands-on workshop for resume writing.', 'workshop', 2, '2025-06-15', '14:00:00', '16:00:00', 'Lab 2', NULL, 40, FALSE);

-- Sample data: event_registrations
INSERT INTO event_registrations (event_id, student_id)
VALUES
(1, 1),
(2, 2);