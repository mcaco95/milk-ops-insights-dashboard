-- Create the database schema for Dairy Operations

-- Dairies table
CREATE TABLE IF NOT EXISTS dairies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    milk_movement_names TEXT[],
    samsara_location_names TEXT[],
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    dairy_id VARCHAR(50) REFERENCES dairies(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert sample dairies based on our actual data
INSERT INTO dairies (id, name, milk_movement_names, samsara_location_names, active) VALUES 
('tk-farms', 'T&K Farms', ARRAY['T&K [Barn 1]', 'T&K [Barn 2]', 'T&K [Barn 3]'], ARRAY['T&K (348) - Barn 1', 'T&K (348) - Barn 2', 'T&K (348) - Barn 3'], true),
('milky-way', 'Milky Way Dairy', ARRAY['Milky Way [North Barn]', 'Milky Way [South Barn]'], ARRAY['Milky Way Dairy'], true),
('triple-g', 'Triple G Main Farm', ARRAY['Triple G [Main Barn]'], ARRAY['Triple G Farm'], true),
('legendairy', 'Legendairy LLC', ARRAY['Legendairy LLC'], ARRAY['Legendairy LLC'], true),
('piazzo', 'Piazzo Dairy', ARRAY['Piazzo Dairy'], ARRAY['Piazzo Dairy'], true),
('dickman', 'Dickman Dairy', ARRAY['Dickman'], ARRAY['Dickman Dairy'], true)
ON CONFLICT (id) DO NOTHING;

-- Insert sample users (passwords are hashed version of 'password123')
-- You should change these passwords in production!
INSERT INTO users (username, password_hash, dairy_id, active) VALUES 
('tkfarms', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'tk-farms', true),
('milkyway', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'milky-way', true),
('tripleg', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'triple-g', true),
('legendairy', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'legendairy', true),
('piazzo', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'piazzo', true),
('dickman', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'dickman', true)
ON CONFLICT (username) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_dairy_id ON users(dairy_id);
CREATE INDEX IF NOT EXISTS idx_dairies_active ON dairies(active);

-- Display the created data
SELECT 'Created dairies:' as info;
SELECT id, name, active FROM dairies;

SELECT 'Created users:' as info;
SELECT id, username, dairy_id, active FROM users; 