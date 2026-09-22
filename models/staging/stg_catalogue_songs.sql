MODEL (
  name staging.stg_catalogue_songs,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column snapshot_date,
    batch_size 1
  ),
  start '2026-01-01',
  end '2026-01-30',
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
WHERE snapshot_date BETWEEN @start_ds AND @end_ds