from pathlib import Path
import streamlit as st  # used only to read secrets safely

# -------- Streamlit page --------
PAGE_TITLE = "RPR Water Level System"
PAGE_LAYOUT = "wide"

# -------- Logos --------
LOGO_DIR = Path("Logos")

PATH_UNI_BONN      = LOGO_DIR / "uni_bonn.jpg"
PATH_EO_AFRICA     = LOGO_DIR / "eoafrica.png"
PATH_DETECT        = LOGO_DIR / "transparent_retina.png"
PATH_TRA           = LOGO_DIR / "tra.png"
PATH_IGG           = LOGO_DIR / "igg.png"
PATH_UPDILIMAN     = LOGO_DIR / "up_diliman.png"
PATH_NIC_CAMERON   = LOGO_DIR / "nic_cameron.jpeg"

# NEW GNSS4SurfaceWater logo
PATH_GNSS4SW       = LOGO_DIR / "gnss4surfacewater.svg"

HEADER_LOGO_WIDTH  = 180
FOOTER_LOGO_WIDTH  = 120

# -------- Map view --------
MAP_INIT_CENTER = (20, 0)   # world view
MAP_INIT_ZOOM   = 2
MAP_HEIGHT_PX   = 580

# -------- WebDAV (Sciebo) --------
WEBDAV_BASE   = st.secrets.get("WEBDAV_BASE", "https://uni-bonn.sciebo.de/public.php/webdav/")
WEBDAV_HOST   = st.secrets.get("WEBDAV_HOST", "https://uni-bonn.sciebo.de")
WEBDAV_FOLDER = st.secrets.get("WEBDAV_FOLDER", "solutions/")
WEBDAV_TOKEN  = st.secrets.get("WEBDAV_TOKEN", "")
WEBDAV_PASS   = st.secrets.get("WEBDAV_PASS", "")

