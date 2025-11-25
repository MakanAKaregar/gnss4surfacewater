import streamlit as st
import pandas as pd
import altair as alt
from streamlit_folium import st_folium

from config import (
    PAGE_TITLE, PAGE_LAYOUT,
    PATH_UNI_BONN, PATH_EO_AFRICA, PATH_DETECT, PATH_TRA,
    PATH_IGG, PATH_UPDILIMAN, PATH_NIC_CAMERON, PATH_GNSS4SW,
    HEADER_LOGO_WIDTH, FOOTER_LOGO_WIDTH,
    MAP_HEIGHT_PX
)
from utils import safe_b64
from parsing import discover_stations, get_series_for
from webdav_client import list_remote_txts, remote_snapshot_hash
from ui_map import build_map


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)

# =========================
# Global STYLES
# =========================
# ---------- GLOBAL CSS FOR YELLOW TABS ----------
st.markdown("""
<style>

/* Yellow rectangular bar */
.stTabs [data-baseweb="tab-list"] {
    background-color: #ffdd33 !important;
    border-radius: 0px !important;      /* rectangular */
    padding: 4px 12px !important;
    gap: 0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #1d3b72 !important;
    font-weight: 700 !important;        /* <-- BOLD TAB NAMES */
    font-size: 0.95rem !important;
    padding: 0.35rem 0.9rem !important;
    border-radius: 6px !important;      
}

/* Hover effect */
.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(255,255,255,0.35) !important;
}

/* Active tab */
.stTabs [aria-selected="true"] {
    background-color: rgba(255,255,255,0.65) !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- GLOBAL CSS For Title text ----------
st.markdown("""
<style>
.rpr-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff !important;
    -webkit-text-stroke: 0.3px #1d3b72;
    text-shadow:
        0 0 2px #1d3b72,
        0 0 4px #1d3b72;
    margin: 0;
    padding: 0;
    white-space: nowrap;   /* prevent text from splitting into two lines */
}
</style>
""", unsafe_allow_html=True)

#--------------------------- Global css for Header & Footer --------------------------
st.markdown("""
<style>
  .block-container { padding-top: 0; padding-bottom: 0; }

  /* Small utility spacer used above charts */
  .chart-spacer{ height:12px; }

  /* Footer layout */
  .footer{ display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:.25rem 0; }
  .footer-left{ font-size:.95rem; color:#444; line-height:1.3; font-weight:400; display:flex; align-items:center; gap:.35rem; }
  .footer-left .at{ opacity:.7; font-weight:700; }
  .footer-right{ display:flex; align-items:center; gap:1rem; flex-wrap:wrap; justify-content:flex-end; }
  .footer-right .caption{ font-size:.85rem; color:#666; white-space:nowrap; }
  .footer-logos{ display:flex; align-items:center; gap:1.2rem; }
  .footer-logos img{ width:60px; height:auto; }

  /* Chips / small section headers */
  .h-chip{
    display:inline-block; background:#e8f4ff; border:1px solid #cfe4ff;
    padding:4px 10px; border-radius:8px; font-weight:600; font-size:1.05rem;
    margin:.25rem 0 .5rem 0;
  }
  .meta-paragraph{ color:#333; font-size:0.95rem; line-height:1.55; margin-bottom:.6rem; font-weight:600; }

  @media (max-width: 900px){
    .footer{ flex-direction:column; align-items:flex-start; gap:.5rem; }
    .footer-right{ justify-content:flex-start; }
  }
</style>
""", unsafe_allow_html=True)

# ---------- MOBILE-RESPONSIVE CSS ----------
# This block makes the layout work nicely on phones and small tablets.
st.markdown("""
<style>
@media (max-width: 768px){

  /* Reduce horizontal padding on mobile */
  .block-container {
      padding-left: 0.7rem !important;
      padding-right: 0.7rem !important;
  }

  /* Stack Streamlit columns vertically */
  .row-widget.stHorizontalBlock, 
  .row-widget.stColumns {
      flex-direction: column !important;
      gap: 0.6rem !important;
  }

  /* Title adjustments */
  .rpr-title {
      font-size: 1.7rem !important;
      text-align: center !important;
      white-space: normal !important;
  }

  /* Sidebar text size */
  section[data-testid="stSidebar"] {
      font-size: 0.9rem !important;
  }

  /* Make tab bar horizontally scrollable on small screens */
  .stTabs [data-baseweb="tab-list"] {
      justify-content: flex-start;
      overflow-x: auto !important;
      padding-bottom: 6px !important;
  }
  .stTabs [data-baseweb="tab"] {
      font-size: 0.85rem !important;
      padding: 0.25rem 0.6rem !important;
      white-space: nowrap;
  }

  /* Logos smaller on mobile */
  .footer-logos img{
      width: 45px !important;
  }

  /* Meta text a bit smaller */
  .meta-paragraph{
      font-size: 0.9rem !important;
  }

  /* Slightly smaller spacer above charts */
  .chart-spacer{
      height: 8px !important;
  }

  /* Folium map height less tall on small screens */
  .folium-map, .st-emotion-cache-1s8y8k0, iframe[title^="st.iframe"] {
      max-height: 360px !important;
  }

  /* Header image responsive */
  img[alt="GNSS4SurfaceWater"] {
      max-width: 140px !important;
      height: auto !important;
  }
}
</style>
""", unsafe_allow_html=True)

# Small helper: ensure header columns also stack on narrow screens
st.markdown("""
<style>
@media (max-width: 768px){
  .row-widget.stColumns {
      flex-direction: column !important;
  }
}
</style>
""", unsafe_allow_html=True)


# =========================
# HEADER and Footer Imgs 
# =========================
uni_bonn_b64      = safe_b64(st, PATH_UNI_BONN,  HEADER_LOGO_WIDTH)
eo_africa_b64     = safe_b64(st, PATH_EO_AFRICA, FOOTER_LOGO_WIDTH)
detect_b64        = safe_b64(st, PATH_DETECT,    FOOTER_LOGO_WIDTH)
tra_b64           = safe_b64(st, PATH_TRA,       FOOTER_LOGO_WIDTH)
igg_b64           = safe_b64(st, PATH_IGG,           FOOTER_LOGO_WIDTH)
up_diliman_b64    = safe_b64(st, PATH_UPDILIMAN,     FOOTER_LOGO_WIDTH)
nic_cameron_b64   = safe_b64(st, PATH_NIC_CAMERON,   FOOTER_LOGO_WIDTH)
gnss4surfacewater_b64 = safe_b64(st, PATH_GNSS4SW, FOOTER_LOGO_WIDTH)

# =========================
# Title Bar
# =========================
col_title, col_info, col_img = st.columns(3, gap="large")
with col_title:
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        """
        <div>
          <h1 class="rpr-title">GNSS4SurfaceWater</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_info:
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        "<span style='color:blue; font-weight:800; font-size:1.25rem; line-height:1.4;'>"
        "Open and real-time operational sea and inland water level observations from ground-based GNSS sites."
        "</span>",
        unsafe_allow_html=True
    )
with col_img:
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            align-items: flex-start;
            height: 100%;
            padding-right: 10px;
        ">
          <img alt="GNSS4SurfaceWater"
               src="data:image/png;base64,{gnss4surfacewater_b64}"
               style="height:{HEADER_LOGO_WIDTH}px;" />
        </div>
        """,
        unsafe_allow_html=True,
    )
    
# =========================
# Side Bar
# =========================
st.sidebar.title("GNSS4SurfaceWater")

with st.sidebar:
    st.markdown(
        """
        <div style="font-size:0.95rem; line-height:1.4;">
            GNSS4SurfaceWater brings together community-driven GNSS-based water-level measurements.
            The platform offers an open space for sharing data related to surface-water monitoring, with a
            particular focus on low-cost GNSS Interferometric Reflectometry (GNSS-IR) sensors such as the
            Raspberry Pi Reflector (RPR), GNSS buoys, and other affordable solutions.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    st.markdown(
        """
        ### Objectives
        * To provide an independent, ground-based service for monitoring current and historical water levels using GNSS.
        * To demonstrate and promote the capabilities of GNSS techniques—including interferometric reflectometry and GNSS buoys—for hydrological applications.
        * To support the use of affordable GNSS instrumentation and encourage broader adoption of GNSS-based monitoring systems.
        * To highlight ongoing projects that use ground-based GNSS for water-level observation.
        * <span style='color:#d9534f; font-weight:600;'>This platform is offered on a best-effort basis for scientific purposes only and no liability of any kind can be assumed.</span>
        """,
        unsafe_allow_html=True
    )


#=======================================
# Insert Nav Bar(Yellow) with Tabs
#=======================================

labels = ["Home", "Data", "Upload Data", "About", "Projects", "Publications", "Contact"]
tab_home, tab_data, tab_upload, tab_about, tab_projects, tab_pubs, tab_contact = st.tabs(labels)

# =========================
# DATA LOAD (Remote WebDAV)
# =========================
_remote_items = list_remote_txts()
_snapshot = remote_snapshot_hash(_remote_items)
stations = discover_stations(_snapshot)

if not stations:
    st.warning("No station .txt files found in the remote folder.")
    st.stop()


# =========================
# CONTENT
# =========================

#--------------------Home--------------------------
with tab_home:
    # Map full width; height controlled in CSS for mobile
    st_folium(build_map(stations), width="100%", height=MAP_HEIGHT_PX)


#--------------------Data--------------------------
with tab_data:
    left, right = st.columns([1, 4], gap="large")

    with left:
        st.markdown("<div class='h-chip'>Select Site</div>", unsafe_allow_html=True)
        site = st.selectbox(
            "Station ID",
            options=sorted(stations.keys()),
            index=0,
            label_visibility="collapsed",
            key="site_select"
        )

        s = stations[site]
        meta, df_all = get_series_for(s["path"], cache_key=s["cache_key"])

        if df_all.empty:
            st.warning("No data available for this station.")
        else:
            min_d = df_all["DateTime"].min().date()
            max_d = df_all["DateTime"].max().date()

            st.markdown("<div class='h-chip'>Select Date Range</div>", unsafe_allow_html=True)
            from_d = st.date_input("From", value=min_d, min_value=min_d, max_value=max_d, key=f"from_{site}")
            to_d   = st.date_input("To",   value=max_d, min_value=min_d, max_value=max_d, key=f"to_{site}")

            if from_d > to_d:
                st.info("‘From’ was after ‘To’. Swapped automatically.")
                from_d, to_d = to_d, from_d

    with right:
        if 'df_all' in locals() and not df_all.empty:
            s = stations[site]
            st.markdown(f"<div class='h-chip'>Station: {site}</div>", unsafe_allow_html=True)

            lat, lon = s["lat"], s["lon"]
            coords = f"{lat:.4f}, {lon:.4f}" if (lat is not None and lon is not None) else "coordinates unavailable"
            water_body = s["meta"].get("water_body") or "Rhine"
            sensor = s["meta"].get("sensor_type") or s["meta"].get("sensor") or "the station's sensor"
            start = df_all["DateTime"].min().date()
            end   = df_all["DateTime"].max().date()

            paragraph = (
                f"This station is located at {water_body} ({coords}) and is operated by University of Bonn. "
                f"It uses {sensor} and its data spans from {start} to {end}."
            )
            st.markdown(f"<div class='meta-paragraph'>{paragraph}</div>", unsafe_allow_html=True)

            vertical_datum = s["meta"].get("vertical_datum") or s["meta"].get("datum")
            if vertical_datum:
                st.markdown(
                    f"<div style='color:#d62728; font-weight:700; margin-top:.25rem;'>"
                    f"Vertical datum: {vertical_datum}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            # Space between any chart title bar and the plot
            st.markdown("<div class='chart-spacer'></div>", unsafe_allow_html=True)

            mask = (df_all["DateTime"].dt.date >= from_d) & (df_all["DateTime"].dt.date <= to_d)
            df_range = df_all.loc[mask].copy()

            if df_range.empty:
                st.warning("No data in the selected date range.")
            else:
                axis = alt.Axis(
                    title="Date",
                    format="%b %d",
                    labelExpr=(
                        "(month(datum.value) == 0 && date(datum.value) <= 7) "
                        "? timeFormat(datum.value, '%b %Y') "
                        ": timeFormat(datum.value, '%b %d')"
                    ),
                    labelOverlap=True,
                    grid=True,
                )

                ymin = float(df_range["Value"].min())
                ymax = float(df_range["Value"].max())
                if ymin == ymax:
                    pad = abs(ymin) * 0.01 if ymin != 0 else 0.01
                    ymin, ymax = ymin - pad, ymax + pad
                else:
                    pad = max(2, (ymax - ymin) * 0.02)
                    ymin, ymax = ymin - pad, ymax + pad

                base_chart = (
                    alt.Chart(df_range)
                    .mark_point(size=25, color="#1f77b4")
                    .encode(
                        x=alt.X("DateTime:T", axis=axis, scale=alt.Scale(nice="month")),
                        y=alt.Y(
                            "Value:Q",
                            title="Water level (meters)",
                            scale=alt.Scale(domain=[ymin, ymax], nice=False, zero=False),
                            axis=alt.Axis(tickCount=6, format="~g", grid=True),
                        ),
                        tooltip=[
                            alt.Tooltip("DateTime:T", title="Date"),
                            alt.Tooltip("Value:Q", title="Water level (m)"),
                        ],
                    )
                    .properties(height=360)
                ).configure_title(offset=12)
                st.altair_chart(base_chart.interactive(), use_container_width=True)


#--------------------Publications--------------------------
with tab_pubs:
    st.header("Publications:")
    st.markdown("""
- Karegar, M. A., Kusche, J., Geremia‐Nievinski, F., & Larson, K. M. (2022). Raspberry Pi Reflector (RPR): A low‐cost water‐level monitoring system based on GNSS interferometric reflectometry. *Water Resources Research*, **58**(12), e2021WR031713.

- Yap, L., Karegar, M. A., Chen, J., Kusche, J. (2025). GNSS-IR monitoring of coastal and river water levels in Cameroon for Sentinel and SWOT altimetry validation. *AGU Fall Meeting Abstracts*, 2025.
""")

#--------------------About--------------------------
with tab_about:

    st.write(
        "GNSS Interferometric Reflectometry (GNSS-IR) was originally applied in an opportunistic manner: environmental "
        "information was extracted from geodetic GNSS reference stations that were never designed to record reflected signals. "
        "Over time, the field has evolved from this indirect use toward purpose-built, low-cost GNSS-IR instrumentation. "
        "Affordable systems such as the Raspberry Pi Reflector (RPR) and other GNSS-IR devices are now specifically designed "
        "and positioned to observe water surfaces with optimized antenna geometry and controlled viewing conditions. This shift "
        "marks a transition from merely detecting reflections when they happened to occur, to intentionally measuring them for "
        "hydrological and environmental applications."
    )

    st.write(
        "At the Institute of Geodesy and Geoinformation (IGG) at the University of Bonn, an international network of RPR "
        "GNSS-IR sensors is operated across several research projects. GNSS4SurfaceWater provides a platform for sharing "
        "water-level time series from affordable GNSS-IR sensors following open-science hardware and software "
        "principles. The platform visualizes ground-based GNSS water-level observations and is "
        "interactive tools for exploring time series, metadata and station characteristics. The community is encouraged to "
        "contribute by uploading their own datasets in the supported format. Instructions for uploading data can be found in the "
        "Upload Data section."
    )

    st.markdown(
        """
        <p style="color:#d9534f; font-weight:600; margin-top:0.8rem;">
        GNSS4SurfaceWater acknowledges funding from the TRA Sustainable Futures: Technology and Innovation for Sustainable Futures
        at the University of Bonn, the ESA EO Africa program, and the Collaborative Research Centre CRC 1502.
        </p>
        """,
        unsafe_allow_html=True
    )

#--------------------Contact--------------------------
with tab_contact:
    st.header("Contact:")
    st.markdown("""
Institute for Geodesy and Geoinformation (IGG)  
Astronomical, Physical and Mathematical Geodesy Group (APMG)  
University of Bonn  
**Address:** Room 2.003, Nußallee 15, 53115 Bonn, Germany  
**Tel:** [+49 (0) 228 73-6160](tel:+49228736160)  
**Email:** [karegar@uni-bonn.de](mailto:karegar@uni-bonn.de)
    """)

#--------------------Upload Data--------------------------
with tab_upload:
    st.header("Upload Data")

    st.markdown("""
The GNSS4SurfaceWater platform welcomes contributions of GNSS-based water-level time series.  
To keep everything consistent and easy to use, all datasets should follow the standard GNSS4SurfaceWater text format described below.

All contributed datasets can be uploaded automatically and on a regular basis to the University of Bonn Sciebo cloud storage (**https://uni-bonn.sciebo.de/**).

To participate in automatic uploads, you should request a **Sciebo WebDAV access token**. Please contact **[Makan Karegar](mailto:karegar@uni-bonn.de)** to obtain your personal token.

---

### 1. File naming convention
All files should follow the naming pattern:

**`<siteID>_<temporalResolution>.txt`**

Examples:
- `cam4_1h.txt`
- `r6gb_2h.txt`
- `rpr1_6h.txt`

---

### 2. Required metadata header
Each file should begin with the following metadata lines and each line starts with `#` and appears exactly in this order:

    # Station: <4-character ID>
    # Location: <City/Region>
    # Latitude: <decimal degrees>
    # Longitude: <decimal degrees>
    # Sensor Type: <sensor/platform>
    # Water Body: <river/lake/coast>
    # Vertical datum: <datum>
    # Units: <units>
    # Provider: <institution(s)>
    # Access Raw Data: <URL or NaN>
    # GNSS Receiver: <model>
    # GNSS Antenna: <model>
    
    
### **3. Data table format** 
After the metadata header, include a comma-separated table with the columns: 
- DateTime — ISO-8601 format (YYYY-MM-DDThh:mm:ss) 
- Height — Water level in the specified units Example:

Examples:

   `DateTime, Height`
      
   `2025-06-01T18:50:18,47.531`
   
   `2025-06-01T20:09:29,47.767`
   
   `2025-06-01T21:44:33,47.801`

### **4. Automatic upload workflow** 

Once you obtain your token, you can configure your server to: 
1. Generate the data file (*.txt) in the required format 
2. Name it according to the standard convention 
3. Use WebDAV to automatically send the file to the GNSS4SurfaceWater cloud directory at daily intervals 
""")

#--------------------Projects--------------------------
with tab_projects:
    st.header("Projects:")
    st.markdown(
        """
            * Cameroon Advanced Measurements for Enhanced Observations of Water levels using Affordable GNSS-IR and Sentinel-3&6 Technology [(CAMEO-WAGST)](https://www.eoafrica-rd.org/research/research-projects-2024-2026/#proposal_8), ESA, EO AFRICA.
            * Collaborative Research Centre CRC1502 [DETECT](https://sfb1502.de/), DFG. 
            * [TRA Sustainable Futures](https://www.uni-bonn.de/en/research-and-teaching/research-profile/transdisciplinary-research-areas/tra-6-sustainable-futures/members-directory/makan-karegar): Technology and Innovation for Sustainable Futures, University of Bonn.
        """
    )

# =========================
# FOOTER
# =========================
st.write("---")
st.markdown(
    f"""
    <div class="footer">
      <div class="footer-left">
        <div class="footer-logos">
          {'<img alt="University of Bonn" src="data:image/png;base64,' + uni_bonn_b64 + '"/>' if uni_bonn_b64 else ''}
          {'<img alt="IGG" src="data:image/png;base64,' + igg_b64 + '"/>' if igg_b64 else ''}
        </div>
      </div>
      <div class="footer-right">
        <div class="footer-logos">
          {'<img alt="NIC Cameron" src="data:image/png;base64,' + nic_cameron_b64 + '"/>' if nic_cameron_b64 else ''}
          {'<img alt="UP Diliman" src="data:image/png;base64,' + up_diliman_b64 + '"/>' if up_diliman_b64 else ''}
          {'<img alt="EO Africa" src="data:image/png;base64,' + eo_africa_b64 + '"/>' if eo_africa_b64 else ''}
          {'<img alt="DETECT" src="data:image/png;base64,' + detect_b64 + '"/>' if detect_b64 else ''}
          {'<img alt="TRA Sustainable Futures" src="data:image/png;base64,' + tra_b64 + '"/>' if tra_b64 else ''}
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

