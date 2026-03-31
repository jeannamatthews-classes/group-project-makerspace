CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
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

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'INFO',
    student_id VARCHAR(20),
    device_id TEXT,
    metadata_json JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX audit_event_type_index ON audit_logs (event_type);
CREATE INDEX audit_created_at_index ON audit_logs (created_at);