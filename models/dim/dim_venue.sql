MODEL (
  name dims.dim_venue,
  kind FULL,
  columns (
    venue_id VARCHAR,
    venue_name VARCHAR,
    city VARCHAR,
    timezone VARCHAR
  )
);

SELECT
    venue_id,
    name AS venue_name,
    city,
    timezone
FROM raw.raw_venues