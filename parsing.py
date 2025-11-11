
import re
from io import StringIO
from pathlib import Path
import pandas as pd
import streamlit as st

from utils import fig_png_b64
from webdav_client import list_remote_txts, remote_snapshot_hash, RemoteTxt

# ---- metadata parsing helpers ----
META_RE = re.compile(r"^#\s*([^:]+)\s*:\s*(.*)$")

def _clean_key(k: str) -> str:
    return k.strip().lower().replace(" ", "_")

# Robust float parser for lat/lon (handles commas, units, etc.)
_num_re = re.compile(r"[-+]?\d+(?:[.,]\d+)?")
def _to_float_any(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    m = _num_re.search(s)
    if not m:
        return None
    return float(m.group(0).replace(",", "."))

@st.cache_data(show_spinner=False)
def load_station_file(_path, cache_key: str):
    """Parse a station .txt (remote path-like) and return (meta, df)."""
    lines = _path.read_text(encoding="utf-8", errors="ignore").splitlines()

    meta = {}
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith("#"):
            m = META_RE.match(line)
            if m:
                meta[_clean_key(m.group(1))] = m.group(2).strip()
        else:
            data_start = i
            break

    if "station" not in meta:
        meta["station"] = _path.stem.split("_")[0]
    meta["file"] = str(_path)

    csv_text = "\n".join(lines[data_start:])
    df = pd.read_csv(StringIO(csv_text), comment="#", sep=None, engine="python")
    df.columns = [c.strip() for c in df.columns]

    dt_col = None
    for pref in ["datetime", "date_time", "date", "time"]:
        for c in df.columns:
            if pref in c.lower():
                dt_col = c; break
        if dt_col: break
    if not dt_col:
        dt_col = df.columns[0]

    val_candidates = [c for c in df.columns if any(k in c.lower() for k in ["height","water_level","level","value"])]
    val_col = val_candidates[0] if val_candidates else (df.columns[1] if len(df.columns) > 1 else None)
    if not val_col:
        raise ValueError(f"Expected a height/value column in {Path(str(_path)).name}")

    df = df[[dt_col, val_col]].rename(columns={dt_col: "DateTime", val_col: "Value"})
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
    df = df.dropna(subset=["DateTime"]).sort_values("DateTime").reset_index(drop=True)
    return meta, df

@st.cache_data(show_spinner=False)
def discover_stations(snapshot_hash: str):
    """Build stations dict from remote WebDAV folder."""
    items = list_remote_txts()
    stations = {}
    for it in items:
        try:
            p = RemoteTxt(name=it["name"], href=it["href"], etag=it["etag"], mtime=it["mtime"], size=it["size"])
            file_key = f'{p.name}|{p.href}|{p.etag}|{p.mtime}|{p.size}'
            meta, df = load_station_file(p, cache_key=file_key)
            sid = str(meta.get("station") or p.stem.split("_")[0])

            lat = None
            for k in ["latitude", "lat", "y", "northing"]:
                lat = _to_float_any(meta.get(k))
                if lat is not None: break
            lon = None
            for k in ["longitude", "lon", "long", "lng", "x", "easting", "longtitude"]:
                lon = _to_float_any(meta.get(k))
                if lon is not None: break

            df_small = df if len(df) <= 600 else df.iloc[:: max(1, len(df)//600)]
            chart_b64 = fig_png_b64(df_small) if not df_small.empty else ""

            stations[sid] = {
                "id": sid, "lat": lat, "lon": lon, "meta": meta, "path": p,
                "n": len(df),
                "t_min": df["DateTime"].min() if not df.empty else None,
                "t_max": df["DateTime"].max() if not df.empty else None,
                "units": meta.get("units") or meta.get("unit") or "",
                "chart_b64": chart_b64,
                "cache_key": file_key,
            }
        except Exception as e:
            import streamlit as st
            st.warning(f"Skipped {it['name']}: {e}")
    return stations

@st.cache_data(show_spinner=False)
def get_series_for(_path, cache_key: str):
    return load_station_file(_path, cache_key)
