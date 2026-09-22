"""Pipeline de reporting repris tel quel du prestataire externe.

Recharge l'integralite des sources a chaque execution (full refresh), execute
les requetes SQL du dossier sql/ dans l'ordre, et publie les tables sous le
schema `reporting` d'une base DuckDB locale (legacy/legacy.duckdb).
"""
from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
SQL_DIR = Path(__file__).resolve().parent / "sql"
DB_PATH = Path(__file__).resolve().parent / "legacy.duckdb"


def latest_catalogue_dir() -> Path:
    days = sorted(p for p in (RAW_DIR / "catalogue").iterdir() if p.is_dir())
    if not days:
        raise SystemExit("Aucun snapshot catalogue trouve dans data/raw/catalogue")
    return days[-1]


def load_sources(con: duckdb.DuckDBPyConnection) -> None:
    catalogue_dir = latest_catalogue_dir()
    print(f"[legacy] catalogue charge depuis le snapshot du {catalogue_dir.name}")

    con.execute(f"""
        CREATE OR REPLACE VIEW raw_app_events AS
        SELECT * FROM read_json_auto('{(RAW_DIR / "app_events" / "*.jsonl").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW latest_songs AS
        SELECT * FROM read_csv_auto('{(catalogue_dir / "songs.csv").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW latest_artists AS
        SELECT * FROM read_csv_auto('{(catalogue_dir / "artists.csv").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW raw_bookings AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "bookings" / "bookings.csv").as_posix()}')
    """)
    con.execute(f"""
        CREATE OR REPLACE VIEW raw_subscriptions AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "subscriptions" / "subscriptions_export.csv").as_posix()}')
    """)


def run_reports(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE SCHEMA IF NOT EXISTS reporting")
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        print(f"[legacy] execution {sql_file.name}")
        con.execute(sql_file.read_text(encoding="utf-8"))


def print_summary(con: duckdb.DuckDBPyConnection) -> None:
    tables = con.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'reporting' ORDER BY 1
    """).fetchall()
    print("\n[legacy] tables de reporting produites :")
    for (table_name,) in tables:
        count = con.execute(f"SELECT COUNT(*) FROM reporting.{table_name}").fetchone()[0]
        print(f"  - reporting.{table_name} ({count} lignes)")


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()  # full refresh : on repart d'une base vide a chaque run
    con = duckdb.connect(str(DB_PATH))
    load_sources(con)
    run_reports(con)
    print_summary(con)
    con.close()
    print(f"\n[legacy] termine. Base : {DB_PATH}")


if __name__ == "__main__":
    main()
