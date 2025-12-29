import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Mall Insight", layout="wide")

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
    st.title("Mall Insight Dashboard")
    st.caption("Landing page utama (metalik hijau). Pilih halaman lain lewat sidebar, atau klik tombol di bawah.")

    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown(
        """
        **Yang ada di project ini:**
        - Page 1: Insight (menu View Dataset, Insight by Parameter, Tren Tahunan, Tren Bulanan)
        - Page lainnya: bisa kamu tambah nanti (misal Correlation / Heatmap, Focus Category, dll)
        """,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.button("➡️ Buka halaman Insight (Page 1)", use_container_width=True)

with c2:
    st.subheader("Preview / Banner")

    # OPSI A (disarankan): taruh gambar di repo, misalnya: assets/banner.png
    local_img = Path("assets/banner.png")

    # OPSI B: kalau kamu taruh di GitHub dan mau pakai URL RAW
    # Ganti string di bawah dengan link RAW gambar kamu
    IMAGE_URL = ""  # contoh: "https://raw.githubusercontent.com/<user>/<repo>/main/assets/banner.png"

    if local_img.exists():
        st.image(str(local_img), use_container_width=True)
    elif IMAGE_URL.strip():
        st.image(IMAGE_URL.strip(), use_container_width=True)
    else:
        st.info("Taruh gambar di `assets/banner.png` atau isi IMAGE_URL (raw GitHub).")

st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.caption("Tip: Sidebar kiri → pilih halaman `Insight` (Page 1).")
