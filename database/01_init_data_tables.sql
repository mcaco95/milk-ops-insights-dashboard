-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist to ensure a clean slate on re-creation
DROP TABLE IF EXISTS volumes_data;
DROP TABLE IF EXISTS routes_data;
DROP TABLE IF EXISTS tanks_data;
DROP TABLE IF EXISTS pickup_logs;

-- =================================================================
--  Tanks Data Table
--  Stores the latest snapshot of each tank's status.
-- =================================================================
CREATE TABLE tanks_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dairy_id VARCHAR(50) NOT NULL REFERENCES dairies(id) ON DELETE CASCADE,
    
    -- Identifying Information
    barn_name VARCHAR(255), -- e.g., "T&K [Barn 1]", "Milky Way"
    tank_name VARCHAR(255) NOT NULL, -- e.g., "Tank 1", "Silo 3"

    -- Volume & Capacity
    current_volume_lbs INT NOT NULL, -- The most up-to-date volume (base + predicted)
    base_volume_lbs INT,             -- The volume from the last manual reading
    predicted_added_lbs INT,         -- Estimated volume added since last reading
    capacity_lbs INT NOT NULL,
    time_to_full_hours FLOAT,        -- Calculated hours until tank reaches capacity

    -- Status Flags
    is_milking BOOLEAN DEFAULT FALSE,
    is_washing BOOLEAN DEFAULT FALSE, -- Legacy flag, may be deprecated

    -- Timestamps
    last_updated TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),
    last_pulled_at TIMESTAMPTZ,       -- Timestamp of the last time milk was taken from this tank
    wash_started_at TIMESTAMPTZ,     -- Timestamp for when the 48-hour wash cycle begins
    
    -- Each tank in a dairy/barn should be unique
    UNIQUE(dairy_id, barn_name, tank_name)
);

CREATE INDEX idx_tanks_data_dairy_id ON tanks_data(dairy_id);
COMMENT ON TABLE tanks_data IS 'Stores periodic snapshots of milk tank levels and statuses from sensor data.';

-- =================================================================
--  Routes Data Table
--  Stores daily route information from Samsara.
-- =================================================================
CREATE TABLE routes_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dairy_id VARCHAR(50) NOT NULL REFERENCES dairies(id) ON DELETE CASCADE,
    
    -- Identifying Information
    samsara_route_id VARCHAR(255), -- Route ID from the source API if available
    report_date DATE NOT NULL,
    
    -- Route Details
    driver_name VARCHAR(255),
    truck_id VARCHAR(100),
    status VARCHAR(50), -- e.g., 'active', 'completed', 'scheduled'
    estimated_arrival TIMESTAMPTZ,
    
    -- New columns to match the desired output
    start_date TIMESTAMPTZ,
    route VARCHAR(255),
    dairy_name VARCHAR(255),
    tank VARCHAR(255),
    processor VARCHAR(255),
    lt_number VARCHAR(255),
    fairlife_number VARCHAR(255),
    tracking_link TEXT,

    -- Timestamps
    last_updated TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),

    -- A route for a specific date and dairy should be unique
    UNIQUE(dairy_id, report_date, samsara_route_id, driver_name, truck_id)
);

CREATE INDEX idx_routes_data_dairy_id_date ON routes_data(dairy_id, report_date);
COMMENT ON TABLE routes_data IS 'Stores daily truck route information from the Samsara API.';

-- =================================================================
--  Volumes Data Table
--  Stores monthly volume totals, broken down by handler/processor.
-- =================================================================
CREATE TABLE volumes_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dairy_id VARCHAR(50) NOT NULL REFERENCES dairies(id) ON DELETE CASCADE,

    -- Identifying Information
    report_month DATE NOT NULL, -- First day of the month, e.g., '2025-05-01'
    handler_name VARCHAR(255) NOT NULL, -- e.g., "Fairlife", "UDA", "Schreiber"

    -- Volume
    total_volume_lbs BIGINT NOT NULL,
    pickup_count INT NOT NULL,

    -- Timestamps
    last_updated TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),

    -- A dairy's volume for a specific month and handler should be unique
    UNIQUE(dairy_id, report_month, handler_name)
);

CREATE INDEX idx_volumes_data_dairy_id_month ON volumes_data(dairy_id, report_month);
COMMENT ON TABLE volumes_data IS 'Stores aggregated monthly milk volumes per handler from the Milk Movement API.';

-- =================================================================
--  Pickup Logs Table
--  Stores raw, individual pickup records for historical export.
-- =================================================================
CREATE TABLE pickup_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dairy_id VARCHAR(50) NOT NULL REFERENCES dairies(id) ON DELETE CASCADE,
    report_month DATE NOT NULL,
    
    -- Raw pickup data to match the CSV format
    pickup_date TIMESTAMPTZ,
    driver_name VARCHAR(255),
    invoice_number VARCHAR(255),
    route_number VARCHAR(255),
    handler_name VARCHAR(255),
    dropoff_weight INT,
    trailer_number VARCHAR(100),
    truck_number VARCHAR(100),

    -- Unique constraint to prevent duplicate entries on reruns
    UNIQUE(dairy_id, report_month, invoice_number)
);

CREATE INDEX idx_pickup_logs_dairy_id_month ON pickup_logs(dairy_id, report_month);
COMMENT ON TABLE pickup_logs IS 'Stores raw, individual pickup records for CSV export.'; 