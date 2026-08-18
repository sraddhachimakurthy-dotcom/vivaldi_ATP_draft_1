CREATE DATABASE IF NOT EXISTS saipravesh
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE saipravesh;

CREATE TABLE IF NOT EXISTS students (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  admission_number  VARCHAR(50)  NOT NULL UNIQUE,
  full_name         VARCHAR(255) NOT NULL,
  email             VARCHAR(255) NULL,
  mobile            VARCHAR(20)  NULL,
  dob               DATE         NULL,
  category          VARCHAR(100) NULL,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  student_id    INT NOT NULL,
  status        VARCHAR(50) NOT NULL DEFAULT 'Started',
  course_level  VARCHAR(100) NULL,
  course_name   VARCHAR(255) NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  application_id    INT NOT NULL UNIQUE,
  screenshot_path   VARCHAR(255) NOT NULL,
  uploaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS health_records (
  id                     INT AUTO_INCREMENT PRIMARY KEY,
  application_id         INT NOT NULL UNIQUE,
  age                    INT NULL,
  height_cm              DECIMAL(5,2) NULL,
  weight_kg              DECIMAL(5,2) NULL,
  blood_group            VARCHAR(5) NULL,
  identification_mark1   VARCHAR(255) NULL,
  identification_mark2   VARCHAR(255) NULL,
  asthma                 VARCHAR(10) DEFAULT 'No',
  diabetes               VARCHAR(10) DEFAULT 'No',
  epilepsy               VARCHAR(10) DEFAULT 'No',
  cardiac                VARCHAR(10) DEFAULT 'No',
  tuberculosis           VARCHAR(10) DEFAULT 'No',
  covid_dose             VARCHAR(50) NULL,
  hep_b                  VARCHAR(10) DEFAULT 'No',
  family_diabetes        VARCHAR(10) DEFAULT 'No',
  family_epilepsy        VARCHAR(10) DEFAULT 'No',
  family_tb              VARCHAR(10) DEFAULT 'No',
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS uploads (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  doc_name     VARCHAR(255) NOT NULL UNIQUE,
  filename     VARCHAR(255) NOT NULL,
  uploaded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);