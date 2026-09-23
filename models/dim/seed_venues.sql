MODEL (
  name dim.seed_venues,
  kind SEED (
    path 'venues_seed.csv'
  ),
  columns (
    venue_id VARCHAR,
    venue_name VARCHAR,
    city VARCHAR,
    timezone VARCHAR
  )
);