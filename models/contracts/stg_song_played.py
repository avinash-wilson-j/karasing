import typing as t
from datetime import datetime

import pandas as pd
from sqlmesh import ExecutionContext, model
from sqlmesh.core.model.kind import ModelKindName


COLUMNS = {
    "event_id": "text",
    "user_id": "text",
    "song_id": "text",
    "session_id": "text",
    "device": "text",
    "country": "text",
    "played_at": "timestamp",
    "duration_sec": "int",
    "completed": "boolean",
}


@model(
    "staging.stg_song_played",
    kind=dict(name=ModelKindName.INCREMENTAL_BY_TIME_RANGE, time_column="played_at"),
    columns=COLUMNS,
    start="2026-01-01",
    end="2026-01-30",
)
def execute(
    context: ExecutionContext,
    start: datetime,
    end: datetime,
    execution_time: datetime,
    **kwargs: t.Any,
) -> pd.DataFrame:
    
    from models.contracts.app_events_v2 import validate_song_played_v2

    table = context.resolve_table("raw.raw_app_events")
    df = context.fetchdf(f"""
        SELECT * FROM {table}
        WHERE event_type = 'song_played'
          AND event_date BETWEEN '{start.date()}' AND '{end.date()}'
    """)

    valid_rows = []
    for _, row in df.iterrows():
        is_valid, _error = validate_song_played_v2(row.to_dict())
        if is_valid:
            valid_rows.append([row.to_dict()[k] for k in COLUMNS])  # ne garde que les colonnes du contrat

    df_valid = pd.DataFrame(valid_rows, columns=list(COLUMNS.keys()))
    return df_valid.drop_duplicates(subset=["event_id"])