MODEL (
  name raw.raw_catalogue_songs,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column snapshot_date,
    batch_size 1
  ),
  start '2026-01-01',
  end '2026-01-30',
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
    *,
    CAST(@start_ds AS DATE) AS snapshot_date
FROM read_csv_auto('data/raw/catalogue/' || @start_ds || '/songs.csv')
