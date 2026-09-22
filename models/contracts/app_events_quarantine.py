import typing as t
from datetime import datetime

import pandas as pd
from sqlmesh import ExecutionContext, model
from sqlmesh.core.model.kind import ModelKindName


COLUMNS = {
    "event_id": "text",
    "raw_payload": "text",
    "validation_error": "text",
    "event_date": "date",
}


@model(
    "staging.app_events_quarantine",
    kind=dict(name=ModelKindName.INCREMENTAL_BY_TIME_RANGE, time_column="event_date"),
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

    quarantine_rows = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        is_valid, error = validate_song_played_v2(row_dict)
        if not is_valid:
            quarantine_rows.append({
                "event_id": row_dict.get("event_id"),
                "raw_payload": str(row_dict),
                "validation_error": error,
                "event_date": row_dict.get("event_date"),
            })

    return pd.DataFrame(quarantine_rows, columns=list(COLUMNS.keys()))