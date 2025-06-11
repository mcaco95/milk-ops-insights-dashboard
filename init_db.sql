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

-- Samsara addresses table (pre-populated to avoid API calls)
CREATE TABLE IF NOT EXISTS samsara_addresses (
    id SERIAL PRIMARY KEY,
    samsara_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address_line_1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_samsara_addresses_name ON samsara_addresses(name);
CREATE INDEX IF NOT EXISTS idx_samsara_addresses_location ON samsara_addresses(latitude, longitude);

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

-- Insert pre-fetched Samsara addresses (to avoid API calls during operations)
INSERT INTO samsara_addresses (samsara_id, name, latitude, longitude, address_line_1, city, state, zip_code) VALUES
  ('119885365', '', 33.34312735285491, -112.70583255748693, '30359 W Old US Hwy 80', 'Palo Verde', 'AZ', '85343'),
  ('120848574', 'Triple G (494) - Barn 1 (Main Barn)', 33.40209012901013, -112.67858970968204, 'C82C+W7 Alder Farms', 'Buckeye', '', ''),
  ('120848694', 'Belmont (701)', 33.539692699956085, -112.88801772243727, '7220 North 387th Avenue', 'Tonopah', '', ''),
  ('120848912', 'T&K (348) - Barn 1 ', 32.883107688075896, -112.02858042494525, 'VXPC+36 Stanfield', 'AZ', '', ''),
  ('120849188', 'PALOMA DAIRY', 32.937492453823225, -112.81896759355455, 'W5QM+3R Gila Bend', 'AZ', '', ''),
  ('120849350', 'AZ Dairy (395)', 32.902977835656486, -112.90512597949098, '38401 W', 'Interstate 8', 'Gila', 'Bend'),
  ('120849626', 'Dickman (815)', 32.94896360075008, -111.58849249351371, '7976 N Tweedy Rd', 'Coolidge', 'AZ', '85128'),
  ('120849913', 'D&I Dairy (805)', 32.99832974255669, -111.59774681586138, '13241 N Curry Rd', 'Coolidge', 'AZ', '85128'),
  ('120850043', 'Saddle Mt. #2 (761)', 33.45945274013766, -112.68827291522771, '29600 West Roosevelt Street', 'Buckeye', '', ''),
  ('120850559', 'Franklin Foods', 32.87802529453582, -111.78378293518773, '1221 West Gila Bend Highway', 'Casa Grande', '', ''),
  ('120850725', 'Casa Grande Dairy Products - 32', 32.878055500901176, -111.78658580079443, '1285 West Gila Bend Highway', 'Casa Grande', '', ''),
  ('120850868', 'Daisy', 32.87377268065441, -111.76834523517037, '752 West Ash Avenue', 'Casa Grande', '', ''),
  ('120851267', 'UDA ', 33.406270242314335, -111.9531482951851, '2008 S Hardy Dr', 'Tempe', 'AZ', '85282'),
  ('120851362', 'ALAMEDA SCALE YARD', 33.401090164118386, -111.95136141053831, '2601 S Hardy Dr', 'Tempe', 'AZ', '85282'),
  ('120851432', 'Vanguard Truck Centers', 33.42493669570277, -112.10181843825202, '2402 South 19th Avenue', 'Phoenix', '', ''),
  ('120851515', 'Shamrock Farms', 33.47257711633055, -112.11504609410125, '2228 North Black Canyon Highway', 'Phoenix', '', ''),
  ('120851628', 'Tolleson Dairy', 33.43854889652926, -112.27674474378605, '500 South 99th Avenue', 'Tolleson', '', ''),
  ('120851699', 'fairlife, LLC', 33.48138594025534, -112.43015567924556, '3100 North Cotton Lane', 'Goodyear', '', ''),
  ('120851779', 'Safeway Milk Plant', 33.39875966487568, -111.95740121917973, '1115 West Alameda Drive', 'Tempe', '', ''),
  ('134041012', 'Milky Way (633)-Barn 1 (North Barn)', 33.063690884333106, -112.13203599684047, '20000 North Ralston Road', 'Maricopa', '', ''),
  ('136758470', 'Legendairy LLC', 33.39470715885537, -112.67557298676299, '28924 W Southern Ave', 'Buckeye', 'AZ', '85326'),
  ('139308005', 'Schreiber', 33.40556347214991, -111.95302665996957, '2122 S Hardy Dr', 'Tempe', 'AZ', '85282'),
  ('139500582', 'Kroger', 33.43926965910112, -112.27667390514594, '500 S 99th Ave', 'Tolleson', 'AZ', '85353'),
  ('141054831', '', 32.91218706668984, -111.97554153757638, 'W26G+VF Stanfield', 'AZ', '', ''),
  ('141055135', 'D & I Holsteins (716)', 32.91216804569247, -111.9740937437777, '3345 N Fuqua Rd', 'Stanfield', 'AZ', '85172'),
  ('152262471', 'Saddle Mt. #3 (761)', 33.3537741595399, -112.65708507908134, '983R+GQ Buckeye', 'AZ', '', ''),
  ('160889177', '', 33.36875144450598, -112.67552830274475, '8605 S Palo Verde Rd', 'Buckeye', 'AZ', '85326'),
  ('170528110', 'Saddle Mt. #1 (761)', 33.34661150749532, -112.70530478042602, '30359 W Old Hwy 80', 'Palo Verde', 'AZ', '85343'),
  ('187431813', 'Arizona Diary', 32.90002983174301, -112.90276637881904, 'W32W+2V Theba', 'AZ', '', ''),
  ('187431816', 'Arizona Diary', 32.90002983174301, -112.90276637881904, 'W32W+2V Theba', 'AZ', '', ''),
  ('188571981', 'Milky Way (633) - Barn 2 (South Barn)', 33.05969817825376, -112.13151221061173, '20000 N Ralston Rd', 'Maricopa', 'AZ', '85139'),
  ('188574911', 'T&K (348) - Barn 2', 32.88720564434537, -112.02922292327881, 'VXPC+36', 'Stanfield', 'AZ', '85172'),
  ('188575331', 'T&K (348) - Barn 3', 32.894259758414464, -112.02892251586914, 'VXPC+36', 'Stanfield', 'AZ', '85172'),
  ('188746182', 'D&I Holsteins (716)', 32.91227770404684, -111.9742442091677, '3345 N Fuqua Rd', 'Stanfield', 'AZ', '85172'),
  ('211704916', 'Du-Brook', 32.91255980862525, -111.65779490796508, '2035 N Overfield Rd', 'Casa Grande', 'AZ', '85194'),
  ('211706049', 'Desperado Dairy', 32.89070092901713, -111.64825620751375, '3179 E Cottonwood Ln', 'Casa Grande', 'AZ', '85194'),
  ('234122207', 'Office', 33.4281338, -111.9729707, '2209 W 1st St #113', 'Tempe', 'AZ', '85281'),
  ('243304678', 'Rainbow Valley Dairy', 33.30754415957162, -112.50926194004384, '14804 S Airport Rd', 'Buckeye', 'AZ', '85326'),
  ('243360323', 'Butterfield Dairy', 33.074158000885205, -112.65658839610879, '40001 W Old Hwy 80', 'Gila Bend', 'AZ', '85337'),
  ('244465190', 'Gasa Grande Dairy Company, LLC', 32.901950433767624, -111.63981670566116, 'W926+HX Casa Grande', 'AZ', '', ''),
  ('250970541', ' #328 Chandler Store', 33.27936350659877, -111.96253043869736, '7001 W Sundust Rd', 'Chandler', 'AZ', '85226'),
  ('250971799', '#659 Tolleson, AZ', 33.45944647242302, -112.24026507128929, '8313 W Roosevelt St', 'Tolleson', 'AZ', '85353'),
  ('250972224', '#280 Buckeye, AZ', 33.43103404016021, -112.5926949940432, '1610 S Miller Rd', 'Buckeye', 'AZ', '85326'),
  ('250972663', '#296 Gila Bend, AZ', 32.944505267389054, -112.73114473581565, '820 W Pima St', 'Gila Bend', 'AZ', '85337'),
  ('251524907', 'EL Dorado Dairy', 32.868652614467365, -111.89245802581641, '29700 W Peters Rd', 'Casa Grande', 'AZ', '85193'),
  ('253245096', '#1575 S Nelson Dr', 33.27725775098875, -111.96105972710193, '1575 S Nelson Dr', 'Chandler', 'AZ', '85226'),
  ('253466386', '#8313 Love Traven Shop', 33.457369849806895, -112.24042600383018, '8313 W Roosevelt St', 'Tolleson', 'AZ', '85353'),
  ('256850079', 'Piazzo Dairy (800)', 33.27092889776911, -112.48642458200075, '19312 South Tuthill Road', 'Buckeye', '', '')
ON CONFLICT (samsara_id) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_dairy_id ON users(dairy_id);
CREATE INDEX IF NOT EXISTS idx_dairies_active ON dairies(active);

-- Display the created data
SELECT 'Created dairies:' as info;
SELECT id, name, active FROM dairies;

SELECT 'Created users:' as info;
SELECT id, username, dairy_id, active FROM users;

SELECT 'Loaded Samsara addresses:' as info;
SELECT COUNT(*) as address_count FROM samsara_addresses; 