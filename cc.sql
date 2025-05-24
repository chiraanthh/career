DROP DATABASE IF EXISTS cc;
CREATE DATABASE cc;
USE cc;

-- Student table with authentication


-- Career Counselor table with authentication
CREATE TABLE career_counselors (
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
    counselor_id INT,
    course VARCHAR(100),
    quiz_result VARCHAR(100) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    date_registered DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    FOREIGN KEY (counselor_id) REFERENCES career_counselors(id) ON DELETE SET NULL
);
-- Administrator table with authentication
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

-- Student grievances
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

-- Counselor assignment logs
CREATE TABLE counselor_assignment_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    old_counselor_id INT,
    new_counselor_id INT NOT NULL,
    reason TEXT,
    assigned_by_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (old_counselor_id) REFERENCES career_counselors(id) ON DELETE SET NULL,
    FOREIGN KEY (new_counselor_id) REFERENCES career_counselors(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_id) REFERENCES administrators(id)
);

-- Appointments
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    counselor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    status ENUM('scheduled', 'completed', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
    mode ENUM('online', 'offline', 'phone') NOT NULL,
    meeting_link VARCHAR(255),
    location VARCHAR(255),
    is_free BOOLEAN DEFAULT FALSE,
    fee DECIMAL(10,2),
    payment_status ENUM('paid', 'pending', 'not_required') DEFAULT 'not_required',
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (counselor_id) REFERENCES career_counselors(id) ON DELETE CASCADE
);

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
    FOREIGN KEY (counsellor_id) REFERENCES career_counselors(id)
);

CREATE TABLE counsellor_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    counsellor_id INT,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    start_time TIME,
    end_time TIME,
    is_recurring BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (counsellor_id) REFERENCES career_counselors(id) ON DELETE CASCADE
);

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

CREATE TABLE student_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    document_type ENUM('transcript', 'resume', 'certificate', 'other') NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_status BOOLEAN DEFAULT FALSE,
    notification_type ENUM('general', 'appointment', 'resource', 'payment', 'grievance') NOT NULL,
    related_entity_id INT,
    FOREIGN KEY (user_id) REFERENCES student(id) ON DELETE CASCADE
);

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

-- GOAL TRACKING
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

CREATE TABLE student_resource_access (
    access_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    resource_id INT,
    access_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (resource_id) REFERENCES career_resources(resource_id) ON DELETE CASCADE
);

-- MILESTONES PER GOAL
CREATE TABLE goal_milestones (
    milestone_id INT AUTO_INCREMENT PRIMARY KEY,
    goal_id INT,
    milestone_title VARCHAR(255),
    due_date DATE,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    FOREIGN KEY (goal_id) REFERENCES career_goals(goal_id) ON DELETE CASCADE
);

-- PUBLIC EVENTS (WORKSHOPS / WEBINARS)
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
    FOREIGN KEY (counsellor_id) REFERENCES career_counselors(id)
);

-- EVENT REGISTRATIONS
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
