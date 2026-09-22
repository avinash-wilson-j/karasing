MODEL (
  name marts.subscription_kpis_monthly,
  kind FULL
);

SELECT
    DATE_TRUNC('month', recorded_at) AS month,
    plan,
    COUNT(*) FILTER (WHERE status = 'active') AS active_count,
    COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_count
FROM facts.fct_subscription_events
GROUP BY 1, 2