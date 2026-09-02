"""Central place for paths and configuration that the backend needs."""

from pathlib import Path

# Path to the data directory, from this file to the project root.
# Inside the container --> data lives at /app/data (see dockerfile).
DATA_DIR = Path(__file__).resolve().parents[3] / "data"
SOLAR_CSV = DATA_DIR / "solar.csv"

# Main solar eclipse types (first letters).
# P = Partial, A = Annular, T = Total, H = Hybrid.
ECLIPSE_TYPE_NAMES = {
    "P": "Partial",
    "A": "Annular",
    "T": "Total",
    "H": "Hybrid",
}
