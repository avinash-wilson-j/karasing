MODEL (
  name raw.raw_subscriptions,
  kind VIEW,
  ignored_rules ["ambiguousorinvalidcolumn"],
  columns (
    user_id VARCHAR,
    plan VARCHAR,
    status VARCHAR,
    started_at VARCHAR,
    cancelled_at VARCHAR,
    recorded_at VARCHAR
  )
);

SELECT * FROM read_csv_auto('data/raw/subscriptions/subscriptions_export.csv')