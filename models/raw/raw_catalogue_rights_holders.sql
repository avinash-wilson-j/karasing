MODEL (
  name raw.raw_catalogue_rights_holders,
  kind FULL,
  columns (
    rights_holder_id VARCHAR,
    name VARCHAR,
    royalty_rate_eur DOUBLE
  )
);

SELECT * FROM read_csv_auto('data/raw/catalogue/2026-01-30/rights_holders.csv')