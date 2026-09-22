MODEL (
  name raw.raw_app_events,
  kind FULL,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    event_id VARCHAR,
    event_type VARCHAR,
    user_id VARCHAR,
    song_id VARCHAR,
    session_id VARCHAR,
    device VARCHAR,
    country VARCHAR,
    played_at VARCHAR,
    searched_at VARCHAR,
    added_at VARCHAR,
    duration_sec BIGINT,
    duration_ms BIGINT,
    completed BOOLEAN,
    query VARCHAR,
    results_count BIGINT,
    _client_seq BIGINT,
    event_date DATE
  )
);

SELECT
    event_id,
    event_type,
    user_id,
    song_id,
    session_id,
    device,
    country,
    played_at,
    searched_at,
    added_at,
    duration_sec,
    duration_ms,
    completed,
    query,
    results_count,
    _client_seq,
    CAST(COALESCE(played_at, searched_at, added_at) AS DATE) AS event_date
FROM read_json_auto('data/raw/app_events/*.jsonl')