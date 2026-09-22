MODEL (
  name raw.raw_catalogue_artists,
  kind FULL,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    artist_id VARCHAR,
    name VARCHAR,
    country VARCHAR
  )
);

SELECT * FROM read_csv_auto('data/raw/catalogue/2026-01-30/artists.csv')