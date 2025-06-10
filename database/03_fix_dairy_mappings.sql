-- =================================================================
--  Fix Dairy Tank Dashboard Name Mappings
--  Updates tank_dashboard_names to match actual form submission names
--  Run this after containers restart to fix existing databases
-- =================================================================

BEGIN;

-- Update dairy mappings to match actual form submission names
UPDATE dairies 
SET tank_dashboard_names = '{"Arizona Dairy"}'
WHERE id = 'az_dairy';

UPDATE dairies 
SET tank_dashboard_names = '{"D&I Coolidge (805)"}'
WHERE id = 'd_i_holsteins';

UPDATE dairies 
SET tank_dashboard_names = '{"D&I Stanfield (716)"}'
WHERE id = 'd_i_dairy';

-- Verify the changes
SELECT id, name, tank_dashboard_names 
FROM dairies 
WHERE id IN ('az_dairy', 'd_i_holsteins', 'd_i_dairy');

COMMIT; 