import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Home", layout="wide")

def load_css(path: str = "assets/mainpage.css"):
    css_path = Path(path)
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file tidak ditemukan: {path}")

load_css()

st.markdown('<div class="hero">', unsafe_allow_html=True)

c1, c2 = st.columns([1.2, 1], gap="large")

with c1:
    st.title("Home — Mall Insight")
    st.caption("Halaman home di folder pages (sinkron dengan app.py).")

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(
        """
        **Navigasi cepat**
        - Buka `Insight (Page 1)` dari sidebar untuk upload CSV & lihat dashboard.
        - Tambahkan halaman lain di folder `pages/` kalau perlu.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.button("✅ Siap! Lanjut ke Insight dari Sidebar", use_container_width=True)

with c2:
    st.subheader("Preview / Banner")
    local_img = Path("assets/banner.png")
    IMAGE_URL = ""  # isi link RAW kalau mau

    if local_img.exists():
        st.image(str(local_img), use_container_width=True)
    elif IMAGE_URL.strip():
        st.image(IMAGE_URL.strip(), use_container_width=True)
    else:
        st.info("Taruh gambar di `assets/banner.png` atau isi IMAGE_URL (raw GitHub).")

st.markdown("</div>", unsafe_allow_html=True)
