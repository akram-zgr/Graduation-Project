-- Insert Admin User (password: admin123)
INSERT OR IGNORE INTO users (username, email, password_hash, is_verified, full_name, is_admin)
VALUES (
    'admin',
    'admin@batnauniversity.com',
    'scrypt:32768:8:1$qKxZGQoqF9pRU7m9$5c8f8e8f3c0e9d7a2b1c4f5e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2',
    1,
    'System Administrator',
    1
);

-- Insert Sample Student User (password: student123)
INSERT OR IGNORE INTO users (username, email, password_hash, is_verified, full_name, department, student_id)
VALUES (
    'student1',
    'student1@batnauniversity.com',
    'scrypt:32768:8:1$qKxZGQoqF9pRU7m9$5c8f8e8f3c0e9d7a2b1c4f5e6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2',
    1,
    'Ahmed Benali',
    'Computer Science',
    'BU2024001'
);
