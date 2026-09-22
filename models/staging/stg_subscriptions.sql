MODEL (
  name staging.stg_subscriptions,
  kind FULL,
  columns (
    user_id VARCHAR,
    plan VARCHAR,
    status VARCHAR,
    started_at DATE,
    cancelled_at DATE,
    recorded_at DATE
  )
);

SELECT
    user_id,
    plan,
    status,
    CAST(started_at AS DATE) AS started_at,
    CAST(cancelled_at AS DATE) AS cancelled_at,
    CAST(recorded_at AS DATE) AS recorded_at
FROM raw.raw_subscriptions