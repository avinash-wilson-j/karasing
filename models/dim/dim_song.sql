MODEL (
  name dims.dim_song,
  kind SCD_TYPE_2_BY_COLUMN (
    unique_key song_id,
    columns [title, artist_id, genre, language, release_year, licensed_until, rights_holder_id],
    disable_restatement false
  )
);

SELECT
    song_id,
    title,
    artist_id,
    genre,
    language,
    release_year,
    licensed_until,
    rights_holder_id
FROM staging.stg_catalogue_songs
QUALIFY ROW_NUMBER() OVER (PARTITION BY song_id ORDER BY snapshot_date DESC) = 1