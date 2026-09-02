"""Central place for paths and configuration that the backend needs."""

from pathlib import Path

#FIX Update: find_data_dir() is not used
# is more robust than assuming the data dir is always 3 levels up from this file.
# Now works even if the backend is run from a different working directory (e.g., in Azure).
def _find_data_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not locate the data directory")

DATA_DIR = _find_data_dir()
SOLAR_CSV = DATA_DIR / "solar.csv"

# Main solar eclipse types (first letters).
# P = Partial, A = Annular, T = Total, H = Hybrid.
ECLIPSE_TYPE_NAMES = {
    "P": "Partial",
    "A": "Annular",
    "T": "Total",
    "H": "Hybrid",
}