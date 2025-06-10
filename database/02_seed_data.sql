-- =================================================================
--  Seed Data
--  Inserts initial data required for the application to be used.
--  This runs *after* all the tables have been created.
-- =================================================================

-- Hashed password for "admin123"
-- Generated using the passlib script:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- print(pwd_context.hash("admin123"))
-- Result: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm'

-- Hashed password for "tk_user_pw"
-- Result: '$2b$12$x/1fB8.jR4lHBeG9tCa0l.s5onrKEvJjO5iJt5yO7d8j2aZ2iE6iW'

BEGIN;

-- 1. Insert Dairies
-- The admin user needs a dairy to be associated with.
INSERT INTO dairies (id, name, active, milk_movement_names, samsara_location_names, tank_dashboard_names) VALUES
('admin_dairy', 'Unassigned (Admin)', true, '{}', '{}', '{}'),
('tk_farms', 'T&K Farms', true, 
    '{"T&K", "T&K Dairy"}', 
    '{"T&K (348) - Barn 1", "T&K (348) - Barn 2", "T&K (348) - Barn 3"}',
    '{"T&K [Barn 1]", "T&K [Barn 2]", "T&K [Barn 3]"}'
),
('milky_way', 'Milky Way Dairy', true, 
    '{"Milky Way Dairy (633)"}', 
    '{"Milky Way (633)-Barn 1 (North Barn)", "Milky Way (633) - Barn 2 (South Barn)"}',
    '{"Milky Way [North Barn]", "Milky Way [South Barn]"}'
),
('triple_g', 'Triple G Dairy', true, 
    '{"Triple G Dairy"}', 
    '{"Triple G (494) - Barn 1 (Main Barn)"}',
    '{"Triple G [Main Barn]"}'
),
('legendairy', 'Legendairy LLC', true, 
    '{"Legendairy LLC"}', 
    '{"Legendairy LLC"}',
    '{"Legendairy LLC"}'
),
('piazzo', 'Piazzo Dairy', true, 
    '{"Piazzo Dairy (800)"}', 
    '{"Piazzo Dairy (800)"}',
    '{"Piazzo Dairy"}'
),
('dickman', 'Dickman Dairy', true, 
    '{"Dickman and Sons Dairy (815)"}', 
    '{"Dickman (815)"}',
    '{"Dickman"}'
),
('belmont', 'Belmont Dairy', true, 
    '{"Belmont Dairy(701)"}', 
    '{"Belmont (701)"}',
    '{"Belmont"}'
),
('d_i_holsteins', 'D & I Holsteins', true, 
    '{"D&I Holsteins (716)"}', 
    '{"D & I Holsteins (716)"}',
    '{"D&I Coolidge (805)"}'
),
('az_dairy', 'AZ Dairy', true, 
    '{"Arizona Dairy"}', 
    '{"AZ Dairy (395)"}',
    '{"Arizona Dairy"}'
),
('d_i_dairy', 'D&I Dairy', true, 
    '{"D&I Dairy (805)"}', 
    '{"D&I Dairy (805)"}',
    '{"D&I Stanfield (716)"}'
)
ON CONFLICT (id) DO UPDATE SET
    milk_movement_names = EXCLUDED.milk_movement_names,
    samsara_location_names = EXCLUDED.samsara_location_names,
    tank_dashboard_names = EXCLUDED.tank_dashboard_names;

-- 2. Insert Users
-- Create the main admin user and a sample dairy user.
INSERT INTO users (username, password_hash, dairy_id, active) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3jp.oFINAm', 'admin_dairy', true),
('tk_user', '$2b$12$x/1fB8.jR4lHBeG9tCa0l.s5onrKEvJjO5iJt5yO7d8j2aZ2iE6iW', 'tk_farms', true)
ON CONFLICT (username) DO NOTHING;

COMMIT; 