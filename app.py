import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Mall Insight", layout="wide")

# =========================
# LOAD CSS (PAKAI insight.css, bukan mainpage.css)
# =========================
def load_css(path: str = "assets/insight.css"):
    css_path = Path(path)
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

load_css()

# =========================
# HEADER
# =========================
st.title("Mall Insight Dashboard")
st.caption("Landing page utama. Gunakan sidebar kiri untuk memilih halaman analisis.")

# =========================
# INFO BOX (gunakan class landing-box dari CSS)
# =========================
st.markdown(
    """
    <div class="landing-box">
        <div style="font-weight:900; font-size:16px; margin-bottom:6px; color:#1F3020;">
            Panduan Cepat
        </div>
        <div style="color:rgba(31,48,32,0.85); line-height:1.55;">
            <b>Mulai dari:</b> <u>Insight (Page 1)</u><br/>
            Di dalamnya ada:
            <ul style="margin:8px 0 0 18px;">
              <li>View Dataset</li>
              <li>Insight by Parameter</li>
              <li>Tren Tahunan</li>
              <li>Tren Bulanan</li>
            </ul>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# =========================
# QUICK LINK KE PAGE INSIGHT (kalau tersedia)
# =========================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Quick Access")
    st.write("Klik untuk langsung menuju halaman Insight.")

    # Streamlit baru punya page_link. Kalau versi kamu belum support, fallback ke info.
    try:
        st.page_link("pages/1_Insight.py", label="➡️ Buka Insight (Page 1)", use_container_width=True)
    except Exception:
        st.info("Buka halaman **Insight (Page 1)** dari sidebar kiri (Pages).")

with col2:
    st.subheader("Preview")
    # Optional: taruh banner lokal
    banner = Path("assets/banner.png")
    if banner.exists():
        st.image(str(banner), use_container_width=True)
    else:
        st.caption("Opsional: taruh gambar di `assets/banner.png` untuk banner.")

st.write("")
st.caption("Catatan: jika tombol quick link tidak muncul, gunakan sidebar kiri → pilih halaman `Insight (Page 1)`.")
