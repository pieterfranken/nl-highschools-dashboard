"""
Data loading and preparation utilities.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Optional
import pandas as pd

from lib.config import (
    DATA_FILE_ACCURATE,
    DATA_FILE_FALLBACK_WITH_COORDS,
    DATA_FILE_RAW,
    CLIENT_FILE,
    ID_COL,
    LAT_COL,
    LON_COL,
    IS_CLIENT_COL,
    RELEVANT_LEVELS,
    IRRELEVANT_LEVELS,
)


def load_clients() -> set[str]:
    if Path(CLIENT_FILE).exists():
        try:
            with open(CLIENT_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_clients(client_ids: set[str]) -> None:
    with open(CLIENT_FILE, "w") as f:
        json.dump(sorted(list(client_ids)), f, indent=2)


def resolve_data_file() -> Path:
    # Prefer accurate coords, then fallback-with-coords, then raw
    if Path(DATA_FILE_ACCURATE).exists():
        return DATA_FILE_ACCURATE
    if Path(DATA_FILE_FALLBACK_WITH_COORDS).exists():
        return DATA_FILE_FALLBACK_WITH_COORDS
    return DATA_FILE_RAW


def load_schools(with_client_flag: bool = True) -> pd.DataFrame:
    df = pd.read_csv(resolve_data_file())

    # Ensure coordinate columns exist
    if LAT_COL not in df.columns:
        df[LAT_COL] = None
    if LON_COL not in df.columns:
        df[LON_COL] = None

    # Filter: keep schools that offer at least one relevant level (VMBO/HAVO/VWO)
    available_relevant = [lvl for lvl in RELEVANT_LEVELS if lvl in df.columns]
    if available_relevant:
        mask = df[available_relevant].astype(bool).any(axis=1)
        df = df[mask].copy()

    # Hide irrelevant level columns from downstream views
    drop_cols = [c for c in IRRELEVANT_LEVELS if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    # Clean levels_offered for display (remove irrelevant tokens)
    if 'levels_offered' in df.columns:
        def _clean_levels(s: object) -> object:
            if isinstance(s, str):
                parts = [p.strip() for p in s.split(',')]
                parts = [p for p in parts if p and p not in IRRELEVANT_LEVELS]
                return ', '.join(parts)
            return s
        df['levels_offered'] = df['levels_offered'].apply(_clean_levels)

    # Attach client flag
    if with_client_flag:
        clients = load_clients()
        df[IS_CLIENT_COL] = df[ID_COL].astype(str).isin(clients)
    return df


def toggle_client(df: pd.DataFrame, school_id: str, make_client: bool) -> set[str]:
    """Update client set and return the updated set"""
    clients = load_clients()
    if make_client:
        clients.add(str(school_id))
    else:
        clients.discard(str(school_id))
    save_clients(clients)
    # also update in-memory df if present
    if IS_CLIENT_COL in df.columns:
        df.loc[df[ID_COL].astype(str) == str(school_id), IS_CLIENT_COL] = make_client
    return clients


def normalize_url(value: object) -> Optional[str]:
    """Ensure website URL is fully-qualified (http/https). Returns None if empty/NaN."""
    try:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        s = str(value).strip()
        if not s or s.lower() == 'nan':
            return None
        if not (s.startswith('http://') or s.startswith('https://')):
            s = 'https://' + s
        return s
    except Exception:
        return None

