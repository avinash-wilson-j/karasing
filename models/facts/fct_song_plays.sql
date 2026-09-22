MODEL (
  name facts.fct_song_plays,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column played_at
  ),
  start '2026-01-01',
  end '2026-01-31',
  columns (
    event_id VARCHAR,
    user_id VARCHAR,
    song_id VARCHAR,
    session_id VARCHAR,
    device VARCHAR,
    country VARCHAR,
    played_at TIMESTAMP,
    duration_sec INT,
    completed BOOLEAN
  )
);

SELECT
    event_id,
    user_id,
    song_id,
    session_id,
    device,
    country,
    played_at,
    duration_sec,
    completed
FROM staging.stg_song_played
WHERE played_at BETWEEN @start_ds AND @end_ds