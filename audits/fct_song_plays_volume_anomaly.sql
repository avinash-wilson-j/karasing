AUDIT (
  name fct_song_plays_volume_anomaly,
  blocking false
);

WITH daily_counts AS (
    SELECT CAST(played_at AS DATE) AS play_date, COUNT(*) AS n
    FROM facts.fct_song_plays
    GROUP BY 1
),
with_rolling AS (
    SELECT
        play_date,
        n,
        AVG(n) OVER (ORDER BY play_date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS avg_7d_prior
    FROM daily_counts
)
SELECT *
FROM with_rolling
WHERE play_date BETWEEN @start_ds AND @end_ds
  AND avg_7d_prior IS NOT NULL
  AND n < 0.5 * avg_7d_prior OR n > 2 * avg_7d_prior