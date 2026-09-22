MODEL (
  name marts.venue_occupancy_daily,
  kind FULL
);

WITH venue_capacity AS (
    SELECT 'venue_lille' AS venue_id, 3 AS n_rooms
    UNION ALL SELECT 'venue_paris', 4
    UNION ALL SELECT 'venue_bruxelles', 2
)
SELECT
    b.venue_id,
    dv.venue_name,
    CAST(b.slot_start_utc AS DATE) AS booking_date,
    COUNT(*) AS bookings_count,
    vc.n_rooms * 7 AS capacity_slots,
    ROUND(COUNT(*)::DOUBLE / (vc.n_rooms * 7), 2) AS occupancy_rate
FROM facts.fct_bar_bookings b
JOIN dims.dim_venue dv ON dv.venue_id = b.venue_id
JOIN venue_capacity vc ON vc.venue_id = b.venue_id
GROUP BY 1, 2, 3, 5