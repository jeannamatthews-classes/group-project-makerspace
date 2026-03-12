

CREATE TABLE students (
id SERIAL PRIMARY KEY,
student_id VARCHAR(20) UNIQUE,
name TEXT NOT NULL,
email TEXT UNIQUE,
card_uid_hash TEXT UNIQUE NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE access_events (
id SERIAL PRIMARY KEY,
student_id VARCHAR(20) REFERENCES students(student_id) NULL,
timestamp TIMESTAMP NOT NULL,
decision VARCHAR(10) NOT NULL CHECK (decision = 'GRANTED' OR decision = 'DENIED'),
reason TEXT,
device_id TEXT,
export_status VARCHAR(10) DEFAULT 'PENDING'
);

CREATE INDEX student_id_index ON access_events (student_id);
CREATE INDEX timestamp_index ON access_events (timestamp);
