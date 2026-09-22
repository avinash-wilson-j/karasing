MODEL (
  name facts.fct_bar_bookings,
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

SELECT * FROM staging.stg_bookings