-- TiDB Schema for EduDrive CRM
-- Converted from PostgreSQL to MySQL/TiDB syntax
-- Execute this in TiDB SQL Editor

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS edudrive_crm;

-- Select the database
USE edudrive_crm;

-- ============================================================================
-- 1. BASE SCHEMA
-- ============================================================================

-- Schools table
CREATE TABLE IF NOT EXISTS schools (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    school_type VARCHAR(50) DEFAULT 'Secondary',
    primary_color VARCHAR(20) DEFAULT '#14213D',
    status VARCHAR(30) DEFAULT 'active',
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_slug (slug)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Roles table with permissions
CREATE TABLE IF NOT EXISTS roles (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    name VARCHAR(80) NOT NULL,
    permissions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    role_id CHAR(36),
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    status VARCHAR(30) DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id),
    INDEX idx_email (email),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- User roles table (for school admin role mapping)
CREATE TABLE IF NOT EXISTS user_roles (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    role VARCHAR(50) NOT NULL,
    school_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_role (user_id, school_id),
    INDEX idx_user_id (user_id),
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Families table
CREATE TABLE IF NOT EXISTS families (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    household_name VARCHAR(150) NOT NULL,
    billing_contact_parent_id CHAR(36),
    status VARCHAR(30) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Parents table
CREATE TABLE IF NOT EXISTS parents (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    family_id CHAR(36),
    full_name VARCHAR(150) NOT NULL,
    relationship VARCHAR(50) DEFAULT 'Parent',
    email VARCHAR(150),
    phone VARCHAR(30),
    preferred_channel VARCHAR(30) DEFAULT 'email',
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_family_id (family_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    name VARCHAR(50) NOT NULL,
    arm VARCHAR(10),
    level_group VARCHAR(50),
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    family_id CHAR(36),
    class_id CHAR(36),
    lead_id CHAR(36),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    admission_no VARCHAR(150) UNIQUE,
    gender VARCHAR(20),
    date_of_birth DATE,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id),
    INDEX idx_family_id (family_id),
    INDEX idx_class_id (class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    parent_name VARCHAR(150) NOT NULL,
    parent_phone VARCHAR(30) NOT NULL,
    parent_email VARCHAR(150),
    source VARCHAR(50) NOT NULL,
    stage VARCHAR(50) DEFAULT 'new',
    interested_class VARCHAR(50),
    follow_up_at TIMESTAMP NULL,
    notes TEXT,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_stage (stage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    student_id CHAR(36),
    invoice_number VARCHAR(50) UNIQUE,
    term VARCHAR(50) NOT NULL,
    amount_due DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(30) DEFAULT 'issued',
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_student_id (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    invoice_id CHAR(36),
    reference VARCHAR(100) UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    student_count INT DEFAULT 0,
    teacher_count INT DEFAULT 0,
    total_persons INT DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    paid_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_reference (reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    family_id CHAR(36),
    parent_id CHAR(36),
    assignee_user_id CHAR(36),
    subject VARCHAR(200) NOT NULL,
    priority VARCHAR(30) DEFAULT 'Medium',
    status VARCHAR(30) DEFAULT 'open',
    sla_due_at TIMESTAMP NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Message logs table
CREATE TABLE IF NOT EXISTS message_logs (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    channel VARCHAR(30) NOT NULL,
    recipient VARCHAR(150) NOT NULL,
    subject VARCHAR(200),
    body TEXT NOT NULL,
    delivery_status VARCHAR(30) DEFAULT 'queued',
    sent_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Activity logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    user_id CHAR(36),
    entity_type VARCHAR(80) NOT NULL,
    entity_id CHAR(36),
    action VARCHAR(120) NOT NULL,
    meta_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    user_id CHAR(36),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Terms/Sessions table
CREATE TABLE IF NOT EXISTS terms (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Fee structures table
CREATE TABLE IF NOT EXISTS fee_structures (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    name VARCHAR(100) NOT NULL,
    class_id CHAR(36),
    term_id CHAR(36),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
    FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Staff table
CREATE TABLE IF NOT EXISTS staff (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    user_id CHAR(36),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(30),
    role VARCHAR(50),
    department VARCHAR(50),
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- PINs table
CREATE TABLE IF NOT EXISTS pins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id CHAR(36),
    pin VARCHAR(20) UNIQUE NOT NULL,
    student_id CHAR(36),
    exam_id INT,
    is_used BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id),
    INDEX idx_pin (pin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- CBT Exams table
CREATE TABLE IF NOT EXISTS cbt_exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id CHAR(36),
    title VARCHAR(200) NOT NULL,
    subject_id CHAR(36),
    duration_minutes INT,
    total_questions INT,
    passing_score INT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(30) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id CHAR(36),
    user_id CHAR(36),
    title VARCHAR(200) NOT NULL,
    message TEXT,
    type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bus routes table
CREATE TABLE IF NOT EXISTS bus_routes (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    route_name VARCHAR(100) NOT NULL,
    driver_name VARCHAR(150),
    driver_phone VARCHAR(30),
    capacity INT,
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    INDEX idx_school_id (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bus stops table
CREATE TABLE IF NOT EXISTS bus_stops (
    id CHAR(36) PRIMARY KEY,
    route_id CHAR(36),
    stop_name VARCHAR(100) NOT NULL,
    stop_order INT,
    time_arrival TIME,
    FOREIGN KEY (route_id) REFERENCES bus_routes(id) ON DELETE CASCADE,
    INDEX idx_route_id (route_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id CHAR(36) PRIMARY KEY,
    school_id CHAR(36),
    key_name VARCHAR(100) NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    UNIQUE KEY unique_setting (school_id, key_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
