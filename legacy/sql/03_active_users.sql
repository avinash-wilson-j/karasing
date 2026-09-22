-- Utilisateurs actifs par jour, a partir des lectures de chansons.
-- _client_seq est l'identifiant de session pose par le SDK mobile : on s'en
-- sert ici comme identifiant d'activite pour compter les utilisateurs uniques.
CREATE OR REPLACE TABLE reporting.active_users_daily AS
SELECT
    CAST(DATE_TRUNC('day', CAST(played_at AS TIMESTAMP)) AS DATE) AS report_date,
    COUNT(DISTINCT _client_seq) AS active_users_count
FROM raw_app_events
WHERE event_type = 'song_played'
GROUP BY 1
ORDER BY 1;
