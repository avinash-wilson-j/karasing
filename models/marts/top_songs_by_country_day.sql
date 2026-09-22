MODEL (
  name marts.top_songs_by_country_day,
  kind FULL
);

SELECT
    fp.country,
    CAST(fp.played_at AS DATE) AS play_date,
    fp.song_id,
    ds.title,
    da.name AS artist_name,
    COUNT(*) AS play_count
FROM facts.fct_song_plays fp
JOIN dims.dim_song ds ON ds.song_id = fp.song_id AND ds.valid_to IS NULL
LEFT JOIN dims.dim_artist da ON da.artist_id = ds.artist_id AND da.valid_to IS NULL
GROUP BY 1, 2, 3, 4, 5