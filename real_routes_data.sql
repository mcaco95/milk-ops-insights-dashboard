-- Clear old data
DELETE FROM routes_data WHERE dairy_id = 'tk_farms' AND report_date = '2025-06-08';

-- Insert REAL route data from actual script output
INSERT INTO routes_data (dairy_id, samsara_route_id, report_date, driver_name, truck_id, status, estimated_arrival, target_location, last_updated) VALUES 
('tk_farms', '183', '2025-06-08', 'Valdes Joseph', '422', 'completed', '2025-06-08 16:31:00', 'T&K - Tank 7', NOW()),
('tk_farms', '128', '2025-06-08', 'Rosko Randy', '423', 'completed', '2025-06-08 17:25:00', 'T&K - Tank 5', NOW()),
('tk_farms', '125', '2025-06-08', 'Allen Shane', '427', 'active', '2025-06-08 19:34:00', 'T&K - Tank 9', NOW());

-- Verify the data
SELECT dairy_id, samsara_route_id, driver_name, truck_id, status, target_location, estimated_arrival 
FROM routes_data 
WHERE dairy_id = 'tk_farms' AND report_date = '2025-06-08' 
ORDER BY estimated_arrival; 