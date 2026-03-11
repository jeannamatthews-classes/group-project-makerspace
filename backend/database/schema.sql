

CREATE TABLE students (
id SERIAL PRIMARY KEY,
student_id VARCHAR(20) UNIQUE,
name TEXT NOT NULL,
email TEXT,
card_uid_hash TEXT UNIQUE NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE access_events (
id SERIAL PRIMARY KEY,
student_id VARCHAR(20) REFERENCES students(student_id),
timestamp TIMESTAMP NOT NULL,
decision VARCHAR(10) NOT NULL,
reason TEXT,
device_id TEXT,
export_status VARCHAR(10) DEFAULT 'PENDING'
);
