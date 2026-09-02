"""Loads and cleans the solar eclipse data.

The data comes from NASA's eclipse catalog and is raw.
Here is where we make it analysis-ready.
"""

import functools

import pandas as pd

from backend.constants import ECLIPSE_TYPE_NAMES, SOLAR_CSV


def _parse_latitude(value: str) -> float | None:
    """'6.0N' -> 6.0, '32.9S' -> -32.9. South becomes negative."""
    value = str(value).strip()
    if not value or value == "-":
        return None
    number = float(value[:-1])
    return -number if value[-1] == "S" else number


def _parse_longitude(value: str) -> float | None:
    """'33.3W' -> -33.3, '10.8E' -> 10.8. West becomes negative."""
    value = str(value).strip()
    if not value or value == "-":
        return None
    number = float(value[:-1])
    return -number if value[-1] == "W" else number


def _parse_year(calendar_date: str) -> int:
    """'-1999 June 12' -> -1999, '3000 October 19' -> 3000.

    Standard date parsers and can't handle years before 1 CE, 
    so we extract the year (enough to show trends over time...).
    """
    return int(str(calendar_date).strip().split()[0])


@functools.lru_cache(maxsize=1)
def load_solar_data() -> pd.DataFrame:
    """Reads solar.csv once, cleans it, caches the result.

    lru_cache = the file is only read and cleaned on the first call;
    after that, same DataFrame is reused for all API requests.
    """
    df = pd.read_csv(SOLAR_CSV)

    # Stripping whitespace from column names just in case.
    df.columns = [c.strip() for c in df.columns]

    # Derive an integer year, group and filter on.
    df["Year"] = df["Calendar Date"].map(_parse_year)

    # Make coordinates numeric so they can be plotted on a map.
    df["Lat"] = df["Latitude"].map(_parse_latitude)
    df["Lon"] = df["Longitude"].map(_parse_longitude)

    # Add a readable type name based on first letters.
    df["Type Name"] = (
        df["Eclipse Type"].str[0].map(ECLIPSE_TYPE_NAMES).fillna("Other")
    )

    return df


def get_records(limit: int | None = None) -> list[dict]:
    """All (or, first `limit`) rows as a list of dicts.

    The frontend uses this for the table and for its own charts.
    """
    df = load_solar_data()
    if limit is not None:
        df = df.head(limit)
    # NaN becomes None -> JSON is valid.
    return df.where(pd.notna(df), None).to_dict(orient="records")


def get_stats() -> dict:
    """Summary metrics for the dashboard's top panel."""
    df = load_solar_data()
    return {
        "total_eclipses": int(len(df)),
        "year_min": int(df["Year"].min()),
        "year_max": int(df["Year"].max()),
        "most_common_type": df["Type Name"].mode()[0],
        "avg_magnitude": round(float(df["Eclipse Magnitude"].mean()), 3),
    }


def get_type_counts() -> list[dict]:
    """Count of eclipses per main type - data for a bar chart."""
    df = load_solar_data()
    counts = df["Type Name"].value_counts()
    return [
        {"type": type_name, "count": int(count)}
        for type_name, count in counts.items()
    ]


def get_counts_by_century() -> list[dict]:
    """Count of eclipses per century - data for a trend line."""
    df = load_solar_data()
    century = (df["Year"] // 100) * 100
    counts = century.value_counts().sort_index()
    return [
        {"century": int(c), "count": int(n)} for c, n in counts.items()
    ]