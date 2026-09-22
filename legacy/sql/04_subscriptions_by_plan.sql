-- Nombre d'abonnes actifs par plan, a date (dernier etat connu par utilisateur).
CREATE OR REPLACE TABLE reporting.subscriptions_by_plan AS
WITH current_state AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY recorded_at DESC) AS rn
    FROM raw_subscriptions
)
SELECT plan, COUNT(*) AS active_subscribers
FROM current_state
WHERE rn = 1 AND status = 'active'
GROUP BY plan
ORDER BY active_subscribers DESC;
