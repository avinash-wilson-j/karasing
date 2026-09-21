MODEL (
  name raw.raw_bookings,
  kind VIEW,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    booking_id VARCHAR,
    venue_id VARCHAR,
    room_id VARCHAR,
    booked_at VARCHAR,
    slot_start VARCHAR,
    party_size INT,
    amount_eur DOUBLE
  )
);

SELECT * FROM read_csv_auto('data/raw/bookings/bookings.csv')