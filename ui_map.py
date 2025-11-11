
import folium
from folium import IFrame
from config import MAP_INIT_CENTER, MAP_INIT_ZOOM

def popup_html_for(sid: str, s: dict) -> str:
    lat = s["lat"]; lon = s["lon"]
    meta = s["meta"]
    location = meta.get("location", "")
    water_body = meta.get("water_body", "")
    provider = meta.get("provider", "University of Bonn")
    sensor   = meta.get("sensor_type") or meta.get("sensor") or ""
    units    = meta.get("units") or meta.get("unit") or ""
    gnss_receiver = meta.get("gnss_receiver") or ""
    gnss_antenna = meta.get("gnss_antenna") or ""

    cov_min  = s["t_min"].date() if s["t_min"] is not None else "-"
    cov_max  = s["t_max"].date() if s["t_max"] is not None else "-"
    npts     = s["n"]
    chart_b64 = s.get("chart_b64", "")

    def row(label, value):
        if value in ("", None): return ""
        return f"<div style='margin:2px 0;'><span style='font-weight:700'>{label}:</span> <span style='font-weight:400'>{value}</span></div>"

    coords = f"{lat:.4f}, {lon:.4f}" if (lat is not None and lon is not None) else ""
    location_line = f"{water_body} ({location})".strip() if water_body else (location or "")
    coverage = f"{cov_min} → {cov_max} ({npts} pts)" if (cov_min != "-" and cov_max != "-") else ""

    chart_block = ""
    toggle_link = ""
    if chart_b64:
        chart_block = f"""
        <div id="chart-{sid}" style="display:none; margin-top:8px;">
          <img src="data:image/png;base64,{chart_b64}" style="width:100%; height:auto; border-radius:6px;"/>
        </div>"""
        toggle_link = f"""
        <a href="#" onclick="
          var el = document.getElementById('chart-{sid}');
          var card = document.getElementById('card-{sid}');
          if(el.style.display==='none'){{ el.style.display='block'; card.style.maxWidth='680px'; }}
          else {{ el.style.display='none'; card.style.maxWidth='440px'; }}
          return false;" 
          style="text-decoration:none; font-weight:600;">View chart →</a>
        """

    html = f"""
    <div id="wrap-{sid}" style="width:700px;">
      <div id="card-{sid}" data-sid="{sid}" style="
          font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
          font-size: 13px; line-height: 1.4; color:#222;
          width:auto; max-width:680px; margin:0;">
        <div id="scroll-{sid}" style="max-height:320px; overflow-y:auto; padding-right:6px;">
          <div style="font-weight:700; margin-bottom:6px;">
             Station: <span style="font-weight:400">{sid}</span>
          </div>
          {row('Water body', water_body)}
          {row('Location', location_line)}
          {row('Lat., Long. (deg.)', coords)}
          {row('Provider', provider)}
          {row('Sensor type', sensor)}
          {row('GNSS receiver', gnss_receiver)}
          {row('GNSS antenna', gnss_antenna)}
          {row('Coverage', coverage)}

          <!-- Add the link before the chart -->
          <div style="margin-top:8px;">
            <a href="https://uni-bonn.sciebo.de/s/pa59z8LHMWWixyp?path=%2Fsolutions"
              target="_blank"
              style="color:#0066cc; font-weight:600; text-decoration:none;">
              Link to raw data →
            </a>
          </div>

          {chart_block}
          <div style="margin-top:8px;">{toggle_link}</div>
        </div>
      </div>
    </div>
    """
    return html

# def build_map(stations_dict: dict) -> folium.Map:
#     m = folium.Map(location=MAP_INIT_CENTER, zoom_start=MAP_INIT_ZOOM, control_scale=True)
#     for sid, s in stations_dict.items():
#         if s["lat"] is None or s["lon"] is None:
#             continue
#         html = popup_html_for(sid, s)
#         iframe = IFrame(html=html, width=700, height=340)
#         pop = folium.Popup(iframe, max_width=720, min_width=360, parse_html=True)
#         folium.Marker(
#             [s["lat"], s["lon"]],
#             popup=pop,
#             tooltip=sid,
#             icon=folium.Icon(color="blue", icon="")
#         ).add_to(m)
#     return m

def build_map(stations_dict: dict) -> folium.Map:
    # Create base map (OpenStreetMap by default)
    m = folium.Map(
        location=MAP_INIT_CENTER,
        zoom_start=MAP_INIT_ZOOM,
        control_scale=True,
        tiles="OpenStreetMap",
        name="Street Map"
    )

    # Add Satellite Layer (Esri World Imagery)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Satellite",
        name="Satellite"
    ).add_to(m)

    # Add all station markers
    for sid, s in stations_dict.items():
        if s["lat"] is None or s["lon"] is None:
            continue

        html = popup_html_for(sid, s)
        iframe = IFrame(html=html, width=700, height=340)
        pop = folium.Popup(iframe, max_width=720, min_width=360, parse_html=True)

        folium.Marker(
            [s["lat"], s["lon"]],
            popup=pop,
            tooltip=sid,
            icon=folium.Icon(color="blue", icon="")
        ).add_to(m)

    # Add layer control (toggle button)
    folium.LayerControl().add_to(m)

    return m
