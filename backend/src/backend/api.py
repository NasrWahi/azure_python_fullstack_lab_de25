"""FastAPI app for eClipseBord.

This is the main entry point for the API.
"""

from fastapi import FastAPI
from backend.src.backend import data_processing

app = FastAPI(title="eClipseBord API", version="1.0.0")


@app.get("/")
def root() -> dict:
    """Simple health check for the API."""
    return {"message": "eClipseBord API is running. See /docs for endpoints."}


@app.get("/eclipses")
def eclipses(limit: int | None = None) -> list[dict]:
    """Cleaned eclipse data. Use ?limit=N to cap the number of rows."""
    return data_processing.get_records(limit=limit)


@app.get("/eclipses/stats")
def stats() -> dict:
    """Summary metrics (count, time span, most common type, etc.)."""
    return data_processing.get_stats()


@app.get("/eclipses/types")
def types() -> list[dict]:
    """Count of eclipses per main type."""
    return data_processing.get_type_counts()


@app.get("/eclipses/by-century")
def by_century() -> list[dict]:
    """Count of eclipses per century."""
    return data_processing.get_counts_by_century()