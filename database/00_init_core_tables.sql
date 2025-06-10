-- =================================================================
--  Core Application Tables
--  These tables are required for the application to function.
-- =================================================================

-- Dairies Table
-- Stores information about each dairy client.
CREATE TABLE dairies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    milk_movement_names TEXT[],
    samsara_location_names TEXT[],
    tank_dashboard_names TEXT[],
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

COMMENT ON TABLE dairies IS 'Stores information about each dairy client.';

-- Users Table
-- Stores user accounts for logging into the system.
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    dairy_id VARCHAR(50) NOT NULL REFERENCES dairies(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX idx_users_username ON users(username);
COMMENT ON TABLE users IS 'Stores user accounts, linking them to a specific dairy.'; 