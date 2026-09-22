MODEL (
  name marts.royalties_monthly,
  kind FULL
);

SELECT
    rh.rights_holder_id,
    rh.name AS rights_holder_name,
    DATE_TRUNC('month', fp.played_at) AS month,
    COUNT(*) AS play_count,
    ROUND(COUNT(*) * ANY_VALUE(rh.royalty_rate_eur), 2) AS royalties_eur
FROM facts.fct_song_plays fp
JOIN dims.dim_song ds ON ds.song_id = fp.song_id AND ds.valid_to IS NULL
JOIN raw.raw_catalogue_rights_holders rh ON rh.rights_holder_id = ds.rights_holder_id
GROUP BY 1, 2, 3