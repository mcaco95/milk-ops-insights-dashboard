-- Fix the routes_data table constraint to prevent duplicates
-- Drop the old complex constraint that allows duplicates
ALTER TABLE routes_data DROP CONSTRAINT routes_data_dairy_id_report_date_samsara_route_id_driver_na_key;

-- Add the correct constraint that ensures one entry per route per dairy per date
ALTER TABLE routes_data ADD CONSTRAINT routes_data_unique_route_per_day 
    UNIQUE (dairy_id, report_date, route);

-- Clean up existing duplicates by keeping only the latest updated entry for each route
WITH ranked_routes AS (
    SELECT id, 
           ROW_NUMBER() OVER (PARTITION BY dairy_id, report_date, route ORDER BY last_updated DESC) as rn
    FROM routes_data
)
DELETE FROM routes_data 
WHERE id IN (
    SELECT id FROM ranked_routes WHERE rn > 1
);

-- Verify the fix
SELECT COUNT(*) as total_routes, 
       COUNT(DISTINCT CONCAT(dairy_id, '-', report_date, '-', route)) as unique_routes
FROM routes_data 
WHERE report_date = '2025-06-10'; 