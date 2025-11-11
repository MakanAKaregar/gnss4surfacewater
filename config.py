
from pathlib import Path
import streamlit as st  # used only to read secrets safely

# -------- Streamlit page --------
PAGE_TITLE = "RPR Water Level System"
PAGE_LAYOUT = "wide"

# -------- Logos --------
LOGO_DIR = Path("Logos")
PATH_UNI_BONN  = LOGO_DIR / "tUN_yzk2_400x400.jpg"
PATH_EO_AFRICA = LOGO_DIR / "EOAFRICA-logo-.png"
PATH_DETECT    = LOGO_DIR / "Logo_DETECT_transparent_retina.png"
PATH_TRA       = LOGO_DIR / "Screenshot_2025-09-29_16-57-12.png"
HEADER_LOGO_WIDTH = 60
FOOTER_LOGO_WIDTH = 60

# -------- Map view --------
MAP_INIT_CENTER = (20, 0)   # world view
MAP_INIT_ZOOM   = 2
MAP_HEIGHT_PX   = 580

# -------- WebDAV (Sciebo) --------
# Read from Streamlit Secrets (set these in the Cloud UI, not in Git)
WEBDAV_BASE   = st.secrets.get("WEBDAV_BASE", "https://uni-bonn.sciebo.de/public.php/webdav/")
WEBDAV_HOST   = st.secrets.get("WEBDAV_HOST", "https://uni-bonn.sciebo.de")
WEBDAV_FOLDER = st.secrets.get("WEBDAV_FOLDER", "solutions/")
WEBDAV_TOKEN  = st.secrets.get("WEBDAV_TOKEN", "")
WEBDAV_PASS   = st.secrets.get("WEBDAV_PASS", "")
