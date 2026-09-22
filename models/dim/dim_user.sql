MODEL (
  name dims.dim_user,
  kind SCD_TYPE_2_BY_TIME (
    unique_key user_id,
    updated_at_name recorded_at,
    disable_restatement false
  )
);

SELECT
    user_id,
    plan,
    status,
    started_at,
    cancelled_at,
    recorded_at
FROM staging.stg_subscriptions
QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY recorded_at DESC) = 1