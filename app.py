import streamlit as st
import pandas as pd
import altair as alt
from streamlit_folium import st_folium

from config import (
    PAGE_TITLE, PAGE_LAYOUT,
    PATH_UNI_BONN, PATH_EO_AFRICA, PATH_DETECT, PATH_TRA,
    PATH_IGG, PATH_UPDILIMAN, PATH_NIC_CAMERON,PATH_GNSS4SW,
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
    color: #ffffff !important;           /* white fill, force override */
    -webkit-text-stroke: 0.3px #1d3b72;    /* dark blue outline */
    text-shadow:
        0 0 2px #1d3b72,
        0 0 4px #1d3b72;                 /* subtle glow */
    margin: 0;
    padding: 0;
}
</style>
""", unsafe_allow_html=True)


#---------------------------Global css for Header & Footer--------------------------
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
gnss4surfacewater_b64      = safe_b64(st, PATH_GNSS4SW, FOOTER_LOGO_WIDTH)

# =========================
# Title Bar
# =========================
col_title, col_info,col_img = st.columns(3, gap="large")
with col_title:
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        f"""
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
            "<span style='color:blue; font-weight:bold;margin-top:20px;'>"
            "Open and real-time operational sea and inland water level observations from ground-based GNSS sites."
            "</span>",
            unsafe_allow_html=True
        )
with col_img:
    st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-end;   /* Push image to the right */
                align-items: flex-start;         /* Align vertically in the middle */
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
            brings together collective GNSS-based water level measurements.
            This platform provides an open space to share data in surface-water monitoring, particularly using
            low-cost GNSS Interferometric Reflectometry (GNSS-IR) sensors such as the Raspberry Pi Reflector,
            GNSS buoys, and other affordable solutions.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.markdown(
        """
        ### Objectives
        * To provide a service that delivers independent, ground-based GNSS monitoring of current and historical water levels.
        * To demonstrate and promote the capabilities of GNSS techniques including interferometric reflectometry and GNSS buoys for monitoring water levels.
        * To encourage the use of affordable GNSS instrumentation, facilitating broader uptake of GNSS-based hydrological monitoring systems.
        * To highlight projects that use ground-based GNSS for water-level monitoring.
        """
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
# CONTENT (Switching in-page by radio)
# =========================

#--------------------Home--------------------------
with tab_home:
    # Map full width
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
                ).configure_title(offset=12)  # adds extra gap below an Altair chart title if you set one
                st.altair_chart(base_chart.interactive(), use_container_width=True)


#--------------------Publications--------------------------
with tab_pubs:
    st.header("Publications:")
    st.markdown("""
- **Karegar, M. A., Kusche, J., Geremia‐Nievinski, F., & Larson, K. M. (2022).**  
  *Raspberry Pi Reflector (RPR): A low‐cost water‐level monitoring system based on GNSS interferometric reflectometry.*  
  *Water Resources Research*, **58**(12), e2021WR031713.

- **Yap, L., Karegar, M. A., Chen, J., Kusche, J. (2025).**  
  *GNSS-IR monitoring of coastal and river water levels in Cameroon for Sentinel and SWOT altimetry validation.*  
  *AGU Fall Meeting Abstracts*, 2025.
""")



#--------------------About--------------------------
with tab_about:
    # st.header("About:")
    st.write(
        "GNSS-IR was first used in an opportunistic way: environmental variables were extracted from geodetic GNSS reference "
        "stations that were never designed to measure reflected signals. Today, the field has moved from this indirect use toward "
        "purpose-built, low-cost GNSS-IR sensing. Affordable sensors such as the Raspberry Pi Reflector (RPR) and other GNSS-"
        "IR devices are now specifically designed and positioned to observe water surfaces under controlled conditions with the "
        "antenna orientation and geometry optimized from the start. This marks a shift from simply using reflections when they "
        "happen to occur to intentionally measuring them for hydrological applications."
    )
    st.write(
        "At the Institute of Geodesy and Geoinformation at the University of Bonn, an international network of RPR GNSS-IR "
        "sensors is operated across a few research projects. GNSS4SurfaceWater serves as a platform for sharing water-level "
        "time series from these affordable GNSS-IR sensors following open-science hardware and software practices and aligned "
        "with FAIR principles The platform visualizes water-level observations from GNSS stations and provides interactive tools "
        "for exploring time series and metadata. The community is encouraged to contribute to this initiative by uploading their "
        "own time series in the supported format. For instructions on how to upload data, please refer to the Data Upload section."
    )


#--------------------Contact--------------------------
with tab_contact:
    st.header("Contact:")
    st.markdown("""
**Institute for Geodesy and Geoinformation (IGG)**  
Astronomical, Physical and Mathematical Geodesy Group (APMG)  
**Address:** Room 2.003, Nußallee 15, 53115, Bonn, Germany.  
**Tel:** [+49 (0) 228 73-6160](tel:+49228736160)  
**Email:** [karegar@uni-bonn.de](mailto:karegar@uni-bonn.de)
""")



#--------------------Upload Data--------------------------
with tab_upload:
    st.header("Upload Data:")
    st.info("Upload a CSV or TXT file to preview and (optionally) append to your repository.")
    upl = st.file_uploader("Choose a CSV/TXT file", type=["csv", "txt"])
    if upl is not None:
        try:
            df = pd.read_csv(upl)
            st.success("File read as CSV.")
            st.dataframe(df.head(200), use_container_width=True)
            st.download_button("Download a copy (CSV)", df.to_csv(index=False).encode(), file_name="uploaded_preview.csv")
        except Exception:
            upl.seek(0)
            text = upl.read().decode("utf-8", errors="ignore")
            st.success("File read as plain text.")
            st.code(text[:5000] + ("\n... (truncated)" if len(text) > 5000 else ""))


#--------------------Projects--------------------------
with tab_projects:
    st.header("Projects:")
    st.markdown(
        """
            * Cameroon Advanced Measurements for Enhanced Observations of Water levels using Affordable GNSS-IR and Sentinel-3&6 Technology (CAMEO-WAGST), ESA, EO AFRICA.
            * DETECT, DFG.
            * TRA Sustainable Futures, University of Bonn.
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






