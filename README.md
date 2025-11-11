# 🌊 RPR Water Level Dashboard

A Streamlit web application for monitoring and visualizing **river and water level data derived from GNSS-based sensors**.  
Developed as part of the EO-Africa / Uni Bonn collaboration.

---

## 🚀 Features

- 📈 Interactive dashboard built with [Streamlit](https://streamlit.io)
- 🗺️ Dynamic maps powered by Folium & Streamlit-Folium  
- 📡 GNSS-based water level monitoring at remote stations  
- 🖼️ Partner logos (Uni Bonn, EO-Africa, DETECT, etc.)
- 🔐 Secure secret management via `.streamlit/secrets.toml`
- ☁️ Ready for one-click deployment on **Streamlit Cloud**

---

## 🧩 Project Structure

```
rpr_dashboard/
├─ app.py                 # Main Streamlit app entry point
├─ config.py              # Configuration (paths, settings)
├─ utils.py               # Helper functions
├─ parsing.py             # Data parsing utilities
├─ webdav_client.py       # WebDAV communication logic
├─ ui_map.py              # Folium map generation
│
├─ Logos/                 # Logo images
│   ├─ EOAFRICA-logo-.png
│   ├─ Logo_DETECT_transparent_retina.png
│   ├─ Screenshot_2025-09-29_16-57-12.png
│   └─ tUN_yzk2_400x400.jpg
│
├─ requirements.txt       # Python dependencies
├─ .gitignore             # Files/folders to ignore
└─ .streamlit/
    └─ secrets.toml       # (local only, not in GitHub)
```


---

## 🛠️ Installation (Local Setup)

```bash
# Clone the repository
git clone  https://github.com/SajjadHussain-UniBonn/rpr-dashboard.git
cd rpr_dashboard

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py

🔐 Secrets Configuration
Before running or deploying, create .streamlit/secrets.toml with:

WEBDAV_BASE   = "https://uni-bonn.sciebo.de/public.php/webdav/"
WEBDAV_HOST   = "https://uni-bonn.sciebo.de"
WEBDAV_FOLDER = "solutions/"
WEBDAV_TOKEN  = "YOUR_TOKEN"
WEBDAV_PASS   = "YOUR_PASSWORD"

⚠️ Never commit this file — it’s already ignored in .gitignore.
In Streamlit Cloud, add these secrets via Settings → Secrets.

```
---



## ☁️ Deployment on Streamlit Cloud

1- Push your project to GitHub.

2- Go to Streamlit Cloud

3- Click New app → Select your repo → Choose app.py as the entry file.

4- Paste your secrets under Settings → Secrets.

5- Click Deploy 🚀

Your app will be live at: https://rpr-dashboard-sajjadhussain-unibonn.streamlit.app


---


## 👥 Credits
Developed by Sajjad Hussain (Uni Bonn)
with support from EO-Africa and DETECT projects.


