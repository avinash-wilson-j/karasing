MODEL (
  name staging.stg_catalogue_songs,
  kind FULL,
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
    snapshot_date
FROM raw.raw_catalogue_songs