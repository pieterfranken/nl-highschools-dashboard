"""
Data loading and preparation utilities.
"""
from __future__ import annotations

from pathlib import Path
import json
import os
import base64
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
    GITHUB_OWNER,
    GITHUB_REPO,
    GITHUB_BRANCH,
    GITHUB_CLIENTS_PATH,
)


def _get_github_token() -> Optional[str]:
    # Try Streamlit session (set via UI)
    try:
        import streamlit as st
        tok = st.session_state.get("GITHUB_TOKEN")
        if tok:
            return tok
        # Then secrets
        tok = st.secrets.get("GITHUB_TOKEN")
        if tok:
            return tok
    except Exception:
        pass
    # Fallback to environment
    return os.environ.get("GITHUB_TOKEN")


def _github_headers(token: str) -> dict:
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}


def load_clients() -> set[str]:
    # Prefer local file for simplicity
    if Path(CLIENT_FILE).exists():
        try:
            with open(CLIENT_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    # On Cloud: try GitHub
    token = _get_github_token()
    if token:
        import requests
        url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_CLIENTS_PATH}?ref={GITHUB_BRANCH}"
        r = requests.get(url, headers=_github_headers(token))
        if r.status_code == 200:
            content = r.json().get("content")
            if content:
                decoded = base64.b64decode(content).decode("utf-8")
                try:
                    return set(json.loads(decoded))
                except Exception:
                    return set()
    return set()


def save_clients(client_ids: set[str]) -> None:
    # Save local (works locally and on Cloud ephemeral FS)
    try:
        with open(CLIENT_FILE, "w") as f:
            json.dump(sorted(list(client_ids)), f, indent=2)
    except Exception:
        pass

    # Also push to GitHub if token available (to persist across Cloud restarts)
    token = _get_github_token()
    if not token:
        return
    import requests
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{GITHUB_CLIENTS_PATH}"

    # Need current SHA if file exists
    sha = None
    r_get = requests.get(url, headers=_github_headers(token), params={"ref": GITHUB_BRANCH})
    if r_get.status_code == 200:
        sha = r_get.json().get("sha")

    payload = {
        "message": "chore(data): update client_schools.json via Streamlit app",
        "content": base64.b64encode(json.dumps(sorted(list(client_ids))).encode("utf-8")).decode("utf-8"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    r_put = requests.put(url, headers=_github_headers(token), json=payload)
    # Swallow errors but could log


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

