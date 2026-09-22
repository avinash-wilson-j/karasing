-- Top des chansons les plus ecoutees, avec l'artiste associe.
CREATE OR REPLACE TABLE reporting.top_songs AS
SELECT
    s.song_id,
    s.title,
    a.name AS artist_name,
    COUNT(*) AS play_count,
    ROUND(AVG(e.duration_sec), 1) AS avg_duration_sec
FROM raw_app_events e
JOIN latest_songs s ON s.song_id = e.song_id
JOIN latest_artists a ON a.artist_id = s.artist_id
WHERE e.event_type = 'song_played'
GROUP BY s.song_id, s.title, a.name
ORDER BY play_count DESC;
