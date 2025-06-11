-- =================================================================
--  Fix Dairy Tank Dashboard Name Mappings
--  Updates tank_dashboard_names to match actual form submission names
--  Run this after containers restart to fix existing databases
-- =================================================================

BEGIN;

-- Update dairy mappings to include BOTH existing names AND actual form submission names
UPDATE dairies 
SET tank_dashboard_names = '{"Arizona Dairy", "AZ Dairy"}'
WHERE id = 'az_dairy';

UPDATE dairies 
SET tank_dashboard_names = '{"D&I Coolidge (805)", "D&I Dairy"}'
WHERE id = 'd_i_dairy';

UPDATE dairies 
SET tank_dashboard_names = '{"D&I Stanfield (716)", "D & I Holsteins"}'
WHERE id = 'd_i_holsteins';

-- Verify the changes
SELECT id, name, tank_dashboard_names 
FROM dairies 
WHERE id IN ('az_dairy', 'd_i_dairy', 'd_i_holsteins')
ORDER BY id;

COMMIT; 