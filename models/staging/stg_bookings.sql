MODEL (
  name staging.stg_bookings,
  kind FULL,
  columns (
    booking_id VARCHAR,
    venue_id VARCHAR,
    room_id VARCHAR,
    slot_start_utc TIMESTAMP,
    party_size INT,
    amount_eur DOUBLE
  )
);

SELECT
    booking_id,
    venue_id,
    room_id,
    CAST(slot_start AS TIMESTAMP) AT TIME ZONE 'Europe/Paris' AT TIME ZONE 'UTC' AS slot_start_utc,
    party_size,
    amount_eur
FROM raw.raw_bookings