AUDIT (
  name fct_song_plays_song_id_exists,
  blocking false
);

SELECT fp.event_id, fp.song_id
FROM facts.fct_song_plays fp
LEFT JOIN dims.dim_song ds ON ds.song_id = fp.song_id AND ds.valid_to IS NULL
WHERE ds.song_id IS NULL
  AND fp.played_at BETWEEN @start_dt AND @end_dt