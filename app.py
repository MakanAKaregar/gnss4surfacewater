import streamlit as st
import pandas as pd
import altair as alt
from streamlit_folium import st_folium

from config import (
    PAGE_TITLE, PAGE_LAYOUT,
    PATH_UNI_BONN, PATH_EO_AFRICA, PATH_DETECT, PATH_TRA,
    PATH_IGG, PATH_UPDILIMAN, PATH_NIC_CAMERON,
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
# SESSION STATE FOR TABS
# =========================
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"


# =========================
# GLOBAL STYLES
# =========================
st.markdown(
    """
<style>
.block-container { padding-top: 0.8rem; }

/* Big title */
.rpr-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff !important;
    -webkit-text-stroke: 0.3px #1d3b72;
    text-shadow: 0 0 2px #1d3b72, 0 0 4px #1d3b72;
    margin: 0;
    padding: 0;
}

/* Separator line */
.separator-line {
    border-top: 1px solid #ccc;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}

/* Nav bar row */
.nav-row {
    margin-bottom: 1.0rem;
}

/* We style each nav button via its key; base style here */
.nav-button-base {
    background-color: #1d3b72;
    color: #f2f2f2;
    font-weight: 600;
    font-size: 0.95rem;
    border-radius: 6px;
    border: none;
    padding: 0.4rem 0.9rem;
}

/* Footer */
.footer{
  display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:.25rem 0;
}
.footer-logos{ display:flex; align-items:center; gap:1.2rem; }
.footer-logos img{ width:60px; height:auto; }

/* Chips / small section headers */
.h-chip{
  display:inline-block; background:#e8f4ff; border:1px solid #cfe4ff;
  padding:4px 10px; border-radius:8px; font-weight:600; font-size:1.05rem;
  margin:.25rem 0 .5rem 0;
}
.meta-paragraph{ color:#333; font-size:0.95rem; line-height:1.55; margin-bottom:.6rem; font-weight:600; }

.chart-spacer{ height:12px; }

@media (max-width: 900px){
  .footer{ flex-direction:column; align-items:flex-start; gap:.5rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# HEADER (LOGOS + TITLE)
# =========================
uni_bonn_b64    = safe_b64(st, PATH_UNI_BONN,      HEADER_LOGO_WIDTH)
eo_africa_b64   = safe_b64(st, PATH_EO_AFRICA,     FOOTER_LOGO_WIDTH)
detect_b64      = safe_b64(st, PATH_DETECT,        FOOTER_LOGO_WIDTH)
tra_b64         = safe_b64(st, PATH_TRA,           FOOTER_LOGO_WIDTH)
igg_b64         = safe_b64(st, PATH_IGG,           FOOTER_LOGO_WIDTH)
up_diliman_b64  = safe_b64(st, PATH_UPDILIMAN,     FOOTER_LOGO_WIDTH)
nic_cameron_b64 = safe_b64(st, PATH_NIC_CAMERON,   FOOTER_LOGO_WIDTH)

col_title, _ = st.columns([3, 3], gap="large")
with col_title:
    st.markdown('<h1 class="rpr-title">GNSS4SurfaceWater</h1>', unsafe_allow_html=True)

st.sidebar.title("GNSS4SurfaceWater")
st.sidebar.markdown(
    """
    <div style="font-size:0.95rem; line-height:1.4;">
        brings together collective GNSS-based water level measurements.
        This platform provides an open space to share data in surface-water monitoring, particularly using
        low-cost GNSS Interferometric Reflectometry (GNSS-IR) sensors such as the Raspberry Pi Reflector,
        GNSS buoys, and other affordable solutions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="separator-line"></div>', unsafe_allow_html=True)


# =========================
# NAVIGATION (BLUE BAR WITH EMOJI ICONS)
# =========================
tabs = [
    ("Home", "🏠 Home"),
    ("Data", "📈 Data"),
    ("Publications", "📚 Publications"),
    ("About", "ℹ️ About"),
    ("Contact", "✉️ Contact"),
    ("Upload Data", "⬆️ Upload Data"),
]

st.markdown('<div class="nav-row">', unsafe_allow_html=True)
nav_cols = st.columns(len(tabs), gap="small")

for i, (tab_key, label) in enumerate(tabs):
    key = f"nav_{tab_key.replace(' ', '_')}"
    is_active = st.session_state.active_tab == tab_key

    with nav_cols[i]:
        if st.button(label, key=key):
            st.session_state.active_tab = tab_key

    # Style this button via CSS
    bg = "#ffcc33" if is_active else "#1d3b72"
    fg = "#1d3b72" if is_active else "#f2f2f2"
    hover_bg = "#e6b800" if is_active else "#355c9a"

    st.markdown(
        f"""
        <style>
        div[data-testid="stButton"][key="{key}"] > button {{
            background-color: {bg} !important;
            color: {fg} !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.4rem 0.9rem !important;
        }}
        div[data-testid="stButton"][key="{key}"] > button:hover {{
            background-color: {hover_bg} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# DATA LOAD (Remote WebDAV, cached)
# =========================
@st.cache_data(show_spinner=True)
def load_stations():
    remote_items = list_remote_txts()
    snapshot = remote_snapshot_hash(remote_items)
    stations_dict = discover_stations(snapshot)
    return stations_dict

stations = load_stations()

if not stations:
    st.warning("No station .txt files found in the remote folder.")
    st.stop()


# Decide map height: medium (max 600)
try:
    map_height = min(int(MAP_HEIGHT_PX), 500)
except Exception:
    map_height = 500


# =========================
# CONTENT BY TAB
# =========================

#--------------------Home--------------------------
if st.session_state.active_tab == "Home":
    with st.spinner("Loading map..."):
        st_folium(build_map(stations), width="900", height=map_height)


#--------------------Data--------------------------
elif st.session_state.active_tab == "Data":
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
            coords = (
                f"{lat:.4f}, {lon:.4f}"
                if (lat is not None and lon is not None)
                else "coordinates unavailable"
            )
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

            # Space between chart title and plot
            st.markdown("<div class='chart-spacer'></div>", unsafe_allow_html=True)

            mask = (df_all["DateTime"].dt.date >= from_d) & (df_all["DateTime"].dt.date <= to_d)
            df_range = df_all.loc[mask].copy()

            if df_range.empty:
                st.warning("No data in the selected date range.")
            else:
                axis = alt.Axis(
                    title="Date",
                    format="%b %d",
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
                        x=alt.X("DateTime:T", axis=axis),
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
elif st.session_state.active_tab == "Publications":
    st.header("Publications:")
    st.markdown("""
- Karegar, M. A., Kusche, J., Geremia‐Nievinski, F., & Larson, K. M. (2022). Raspberry Pi Reflector (RPR): A low‐cost water‐level monitoring system based on GNSS interferometric reflectometry.*Water Resources Research*, 58(12), e2021WR031713.

- Yap, L., Karegar, M. A., Chen, J., Kusche, J. (2025). GNSS-IR monitoring of coastal and river water levels in Cameroon for Sentinel and SWOT altimetry validation. *AGU Fall Meeting Abstracts*, 2025.
""")


#--------------------About--------------------------
elif st.session_state.active_tab == "About":
    st.write(
        "GNSS-IR was first used in an opportunistic way: environmental variables were extracted from geodetic GNSS reference "
        "stations that were never designed to measure reflected signals. Today, the field has moved from this indirect use toward "
        "purpose-built, low-cost GNSS-IR sensing. Affordable sensors such as the Raspberry Pi Reflector (RPR) and other GNSS-"
        "IR devices are now specifically designed and positioned to observe water surfaces under controlled conditions with the "
        "antenna orientation and geometry optimized from the start. This marks a shift from simply using reflections when they "
        "happen to occur to intentionally measuring them for hydrological applications."
    )
    st.markdown(
        "At the [Institute of Geodesy and Geoinformation at the University of Bonn](https://www.igg.uni-bonn.de), "
        "an international network of RPR GNSS-IR sensors is operated across a few research projects. GNSS4SurfaceWater serves "
        "as a platform for sharing water-level time series from these affordable GNSS-IR sensors following open-science hardware "
        "and software practices and aligned with FAIR principles. The platform visualizes water-level observations from GNSS "
        "stations and provides interactive tools for exploring time series and metadata. The community is encouraged to contribute "
        "to this initiative by uploading their own time series in the supported format. For instructions on how to upload data, "
        "please refer to the Data Upload section."
    )


#--------------------Contact--------------------------
elif st.session_state.active_tab == "Contact":
    st.header("Contact")

    st.markdown("""
**Dr. Makan Karegar**  
Institute for Geodesy and Geoinformation (IGG)  
Astronomical, Physical and Mathematical Geodesy Group (APMG)  
University of Bonn  

**Address:** Room 2.003, Nußallee 15, 53115 Bonn, Germany  
**Tel:** [+49 (0) 228 73-6160](tel:+49228736160)  
**Email:** [karegar@uni-bonn.de](mailto:karegar@uni-bonn.de)
    """)



#--------------------Upload Data--------------------------
elif st.session_state.active_tab == "Upload Data":
    st.header("Upload Data")

    st.markdown("""
    The GNSS4SurfaceWater platform welcomes contributions of GNSS-based water-level time series. To ensure consistency and interoperability, all datasets should follow the **standard GNSS4SurfaceWater text format** described below.

    ### **Notice**
    All contributed datasets are uploaded **automatically on a regular basis** to the University of Bonn Sciebo cloud storage (**https://uni-bonn.sciebo.de/**).

    To participate in automatic uploads, you need a **Sciebo WebDAV access token**. Please contact **[Makan Karegar](mailto:karegar@uni-bonn.de)** to obtain your personal token.

    ---

    ## **1. File naming convention**
    All files must follow the naming pattern:

    **`<siteID>_<temporalResolution>.txt`**

    Examples:
    - `cam4_1h.txt`
    - `r6gb_30m.txt`
    - `rpr1_5m.txt`

    ---

    ## **2. Required metadata header**
    Each file must begin with the following metadata lines, each starting with `#` and appearing **exactly in this order**:

    ```
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
    #
    ```

    ---

    ## **3. Data table format**

    After the metadata header, include a comma-separated table with the columns:

    - `DateTime` — ISO-8601 format (`YYYY-MM-DDThh:mm:ss`)
    - `Height` — Water level in the specified units

    Example:

    ```
    DateTime,Height
    2025-06-01T18:50:18,47.531
    2025-06-01T20:09:29,47.767
    2025-06-01T21:44:33,47.801
    ```

    ---

    ## **4. Automatic upload workflow**

    Once you obtain your token, you can configure your device or server to:

    1. Generate the data file (`*.txt`) in the required format  
    2. Name it according to the standard convention  
    3. Use WebDAV to automatically send the file to the GNSS4SurfaceWater cloud directory  
       at regular intervals (hourly, daily, or real-time)
    """)


# =========================
# FOOTER
# =========================
st.write("---")
st.markdown(
    f"""
    <div class="footer">
      <div class="footer-logos">
        {'<img alt="University of Bonn" src="data:image/png;base64,' + uni_bonn_b64 + '"/>' if uni_bonn_b64 else ''}
        {'<img alt="IGG" src="data:image/png;base64,' + igg_b64 + '"/>' if igg_b64 else ''}
      </div>
      <div class="footer-logos">
        {'<img alt="NIC Cameron" src="data:image/png;base64,' + nic_cameron_b64 + '"/>' if nic_cameron_b64 else ''}
        {'<img alt="UP Diliman" src="data:image/png;base64,' + up_diliman_b64 + '"/>' if up_diliman_b64 else ''}
        {'<img alt="EO Africa" src="data:image/png;base64,' + eo_africa_b64 + '"/>' if eo_africa_b64 else ''}
        {'<img alt="DETECT" src="data:image/png;base64,' + detect_b64 + '"/>' if detect_b64 else ''}
        {'<img alt="TRA Sustainable Futures" src="data:image/png;base64,' + tra_b64 + '"/>' if tra_b64 else ''}
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

