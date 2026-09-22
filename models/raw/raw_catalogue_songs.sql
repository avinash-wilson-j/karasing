MODEL (
  name raw.raw_catalogue_songs,
  kind FULL,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    song_id VARCHAR,
    title VARCHAR,
    artist_id VARCHAR,
    genre VARCHAR,
    language VARCHAR,
    release_year INT,
    licensed_until DATE,
    rights_holder_id VARCHAR,
    snapshot_date DATE
  )
);

SELECT
    song_id,
    title,
    artist_id,
    genre,
    language,
    release_year,
    licensed_until,
    rights_holder_id,
    CAST(regexp_extract(filename, '(\d{4}-\d{2}-\d{2})') AS DATE) AS snapshot_date
FROM read_csv_auto('data/raw/catalogue/*/songs.csv', filename=true)