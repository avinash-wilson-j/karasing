MODEL (
  name raw.raw_venues,
  kind VIEW,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    venue_id VARCHAR,
    name VARCHAR,
    city VARCHAR,
    timezone VARCHAR
  )
);

SELECT * FROM read_csv_auto('data/raw/bookings/venues.csv')