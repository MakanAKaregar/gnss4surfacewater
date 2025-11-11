
from PIL import Image
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def image_to_base64(path, width: int | None = None) -> str:
    img = Image.open(path)
    if width and img.width:
        r = width / img.width
        img = img.resize((int(width), int(img.height * r)))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def safe_b64(st, path, width: int | None = None) -> str:
    try:
        return image_to_base64(path, width)
    except Exception as e:
        st.warning(f"Logo missing or unreadable: {path} ({e})")
        return ""

def fig_png_b64(df):
    """Render compact matplotlib line chart (DateTime vs Value) to base64 PNG."""
    fig, ax = plt.subplots(figsize=(6.0, 2.6), dpi=110)
    ax.plot(df["DateTime"], df["Value"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Water level (m)")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(mdates.AutoDateLocator()))
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    import base64 as _b64
    return _b64.b64encode(buf.getvalue()).decode()
