-- Migration: Create users table for password management
-- Date: 2025-12-23
-- Description: Add users table with hashed passwords for authentication
-- Author: WebIAScrap Team

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_password_change TIMESTAMP
);

-- Create index on username for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Insert default admin user
-- Password: changeme
-- Hash generated with: python3 scripts/generate_admin_hash.py changeme
INSERT INTO users (username, password_hash, created_at)
VALUES (
    'admin',
    'pbkdf2:sha256:1000000$Q5S0HmDHohNF5xGS$4bd82b1a3117024bc40a7e2ffc6d8b14547d393967ed72beef0246d76bfbcccd',
    CURRENT_TIMESTAMP
)
ON CONFLICT (username) DO NOTHING;

-- Add comments
COMMENT ON TABLE users IS 'Usuarios del sistema con contraseñas hasheadas (PBKDF2-HMAC-SHA256)';
COMMENT ON COLUMN users.password_hash IS 'Hash de contraseña generado con werkzeug.security (pbkdf2:sha256)';
COMMENT ON COLUMN users.last_password_change IS 'Timestamp del último cambio de contraseña';

-- Verify the table was created
-- Run after migration: SELECT * FROM users;
