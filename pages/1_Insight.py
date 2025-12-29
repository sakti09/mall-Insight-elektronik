import streamlit as st
import pandas as pd

st.set_page_config(page_title="Insight", layout="wide")

# =========================
# CSS (UI Styling)
# =========================
def inject_card_css():
    st.markdown(
        """
        <style>
        /* ===== Page background ===== */
        .stApp {
            background-color: #ffffff;
        }

        /* ===== Title styling ===== */
        h1, h2, h3 {
            color: #1F3020;
        }

        /* ===== Caption text ===== */
        .stCaption {
            color: rgba(31,48,32,0.75);
        }

        /* ===== Dataframe styling ===== */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            padding: 8px;
            background-color: #FAFAFA;
        }

        /* ===== Card button base ===== */
        .card button {
            width: 100% !important;
            height: 92px !important;
            border-radius: 18px !important;
            border: none !important;
            color: white !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            text-align: left !important;
            padding: 16px 18px !important;
            white-space: pre-line !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.10) !important;
        }

        .card button:hover {
            filter: brightness(1.05);
            transform: translateY(-2px);
            transition: all 0.15s ease-in-out;
        }

        /* ===== Card color variants ===== */
        .card-1 button { background: linear-gradient(135deg, #3A4A3B, #1F3020) !important; }
        .card-2 button { background: linear-gradient(135deg, #698A6B, #3A4A3B) !important; }
        .card-3 button { background: linear-gradient(135deg, #A9C2AA, #698A6B) !important; color:#0F1C10 !important; }
        .card-4 button { background: linear-gradient(135deg, #1F3020, #0F1C10) !important; }
        .card-5 button { background: linear-gradient(135deg, #0F1C10, #3A4A3B) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ⬅️ WAJIB dipanggil sebelum UI
inject_card_css()

st.title("Page 1 — Insight Dashboard")

# =========================
# Load data
# =========================
uploaded = st.file_uploader("Upload CSV (final insight)", type=["csv"])
if not uploaded:
    st.info("Upload CSV dulu untuk melihat dashboard insight.")
    st.stop()

df = pd.read_csv(uploaded)

# =========================
# Router subpage (inside Page 1)
# =========================
if "insight_subpage" not in st.session_state:
    st.session_state.insight_subpage = "home"

def go(page_name: str):
    st.session_state.insight_subpage = page_name

def card_button(label: str, key: str, on_click_page: str, color_class="card-1", disabled=False):
    btn_label = f"{label}\n\nKlik untuk buka"
    st.markdown(f'<div class="card {color_class}">', unsafe_allow_html=True)
    if st.button(btn_label, key=key, disabled=disabled, use_container_width=True):
        go(on_click_page)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# HOME (menu kartu)
# =========================
if st.session_state.insight_subpage == "home":
    st.subheader("Menu (Page 1)")
    st.caption("Klik kartu di bawah untuk membuka sub-halaman (masih di Page 1).")

    cols = st.columns(5)
    with cols[0]:
        card_button("1) View Dataset", "card_1", "view_dataset", color_class="card-1")
    with cols[1]:
        card_button("2) Insight by Parameter", "card_2", "insight_param", color_class="card-2")
    with cols[2]:
        card_button("3) Placeholder", "card_3", "todo_3", color_class="card-3", disabled=True)
    with cols[3]:
        card_button("4) Placeholder", "card_4", "todo_4", color_class="card-4", disabled=True)
    with cols[4]:
        card_button("5) Placeholder", "card_5", "todo_5", color_class="card-5", disabled=True)

    cols2 = st.columns(5)
    with cols2[0]:
        card_button("6) Placeholder", "card_6", "todo_6", color_class="card-1", disabled=True)
    with cols2[1]:
        card_button("7) Placeholder", "card_7", "todo_7", color_class="card-2", disabled=True)
    with cols2[2]:
        card_button("8) Placeholder", "card_8", "todo_8", color_class="card-3", disabled=True)
    with cols2[3]:
        card_button("9) Placeholder", "card_9", "todo_9", color_class="card-4", disabled=True)
    with cols2[4]:
        card_button("10) Placeholder", "card_10", "todo_10", color_class="card-5", disabled=True)

    st.markdown("---")
    st.caption("Preview data:")
    st.dataframe(df.head(5), use_container_width=True)

# =========================
# SUBPAGE: VIEW DATASET
# =========================
elif st.session_state.insight_subpage == "view_dataset":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("⬅️ Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("View Dataset")

    st.caption("Tabel data lengkap yang dapat diurutkan (sorting).")

    sort_cols = df.columns.tolist()
    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        default_idx = sort_cols.index("age") if "age" in sort_cols else 0
        sort_by = st.selectbox("Sort by column", options=sort_cols, index=default_idx)

    with c2:
        ascending = st.radio("Order", ["Ascending", "Descending"], horizontal=True)

    with c3:
        n_rows = st.slider("Jumlah baris ditampilkan", 10, 500, 100)

    df_sorted = df.sort_values(by=sort_by, ascending=(ascending == "Ascending"))

    st.markdown("---")
    st.caption("Hasil data setelah sorting:")
    st.dataframe(df_sorted.head(n_rows), use_container_width=True, height=520)

# =========================
# SUBPAGE: INSIGHT PARAM (placeholder)
# =========================
elif st.session_state.insight_subpage == "insight_param":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("⬅️ Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("Insight by Parameter")
    st.info("Bagian ini akan berisi chart & filter parameter.")

else:
    go("home")
