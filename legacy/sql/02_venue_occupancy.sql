-- Occupation quotidienne des 3 bars. Les horaires de reservation arrivent en
-- heure locale depuis la caisse de chaque bar : on les convertit en UTC
-- avant d'agreger, pour rester coherent avec le reste du pipeline (qui est
-- en UTC partout ailleurs).
CREATE OR REPLACE TABLE reporting.venue_occupancy_daily AS
SELECT
    venue_id,
    CAST(DATE_TRUNC('day', CAST(slot_start AS TIMESTAMP) + INTERVAL 1 HOUR) AS DATE) AS report_date,
    COUNT(*) AS bookings_count,
    SUM(party_size) AS total_party_size,
    ROUND(AVG(amount_eur), 2) AS avg_amount_eur
FROM raw_bookings
GROUP BY 1, 2
ORDER BY 1, 2;
