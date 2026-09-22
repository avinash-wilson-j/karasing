MODEL (
  name facts.fct_subscription_events,
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

SELECT * FROM staging.stg_subscriptions