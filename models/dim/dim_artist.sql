MODEL (
  name dims.dim_artist,
  kind SCD_TYPE_2_BY_COLUMN (
    unique_key artist_id,
    columns [name, country],
    disable_restatement false
  )
);

SELECT
    artist_id,
    name,
    country
FROM raw.raw_catalogue_artists