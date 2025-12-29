import streamlit as st
import pandas as pd

st.set_page_config(page_title="Insight", layout="wide")

#CSS
def inject_card_css():
    st.markdown(
        """
        <style>

        /* ===== Page background (tetap putih tapi lembut) ===== */
        .stApp {
            background-color: #ffffff;
        }

        /* ===== Title styling ===== */
        h1, h2, h3 {
            color: #1F3020;
        }

        /* ===== Section container ===== */
        .block-container {
            padding-top: 2rem;
        }

        /* ===== Dataframe styling ===== */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            padding: 8px;
            background-color: #FAFAFA;
        }

        /* ===== Card base style ===== */
        div.stButton > button {
            width: 100%;
            height: 92px;
            border-radius: 18px;
            border: none;
            color: white;
            font-size: 14px;
            font-weight: 600;
            text-align: left;
            padding: 16px 18px;
            white-space: pre-line;
            box-shadow: 0 8px 20px rgba(0,0,0,0.10);
        }

        div.stButton > button:hover {
            filter: brightness(1.05);
            transform: translateY(-2px);
            transition: all 0.15s ease-in-out;
        }

        /* ===== CARD COLOR VARIANTS ===== */
        .card-1 > button { background: linear-gradient(135deg, #3A4A3B, #1F3020); }
        .card-2 > button { background: linear-gradient(135deg, #698A6B, #3A4A3B); }
        .card-3 > button { background: linear-gradient(135deg, #A9C2AA, #698A6B); color:#0F1C10; }
        .card-4 > button { background: linear-gradient(135deg, #1F3020, #0F1C10); }
        .card-5 > button { background: linear-gradient(135deg, #0F1C10, #3A4A3B); }

        </style>
        """,
        unsafe_allow_html=True,
    )

inject_card_css()

st.title("Page 1 — Insight Dashboard")

# Load data
uploaded = st.file_uploader("Upload CSV (final insight)", type=["csv"])
if not uploaded:
    st.info("Upload CSV dulu untuk melihat dashboard insight.")
    st.stop()

df = pd.read_csv(uploaded)


# Router subpage (dalam Page 1)
if "insight_subpage" not in st.session_state:
    st.session_state.insight_subpage = "home"

def go(page_name: str):
    st.session_state.insight_subpage = page_name

def card_button(label: str, emoji: str, key: str, on_click_page: str, color_class="card-1", disabled=False):
    btn_label = f"{emoji}  {label}\n\nKlik untuk buka"
    with st.container():
        st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
        if st.button(btn_label, key=key, disabled=disabled, use_container_width=True):
            go(on_click_page)
        st.markdown("</div>", unsafe_allow_html=True)


# HOME (grid 10 kartu)
if st.session_state.insight_subpage == "home":
    st.subheader("Menu (Page 1)")
    st.caption("Klik kartu di bawah untuk membuka sub-halaman (masih di Page 1).")

    cols = st.columns(5)
    with cols[0]:
        card_button("1) View Dataset", "card_1", "view_dataset", color_class="card-1")
    with cols[1]:
        card_button("2) Insight by Parameter",, "card_2", "insight_param", color_class="card-2")
    with cols[2]:
        card_button("3) Placeholder", , "card_3", "todo_3", color_class="card-3", disabled=True)
    with cols[3]:
        card_button("4) Placeholder",, "card_4", "todo_4", color_class="card-4", disabled=True)
    with cols[4]:
        card_button("5) Placeholder",, "card_5", "todo_5", color_class="card-5", disabled=True)


    cols2 = st.columns(5)
    with cols2[0]:
        card_button("6) Placeholder",, "card_6", "todo_6", disabled=True)
    with cols2[1]:
        card_button("7) Placeholder",, "card_7", "todo_7", disabled=True)
    with cols2[2]:
        card_button("8) Placeholder",, "card_8", "todo_8", disabled=True)
    with cols2[3]:
        card_button("9) Placeholder",, "card_9", "todo_9", disabled=True)
    with cols2[4]:
        card_button("10) Placeholder",, "card_10", "todo_10", disabled=True)

    st.markdown("---")
    st.write("Preview cepat dataset (top 5):")
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

    # ===== Sorting Controls =====
    sort_cols = df.columns.tolist()
    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        default_idx = sort_cols.index("age") if "age" in sort_cols else 0
        sort_by = st.selectbox("Sort by column", options=sort_cols, index=default_idx)

    with c2:
        ascending = st.radio(
            "Order",
            options=["Ascending", "Descending"],
            horizontal=True
        )

    with c3:
        n_rows = st.slider(
            "Jumlah baris ditampilkan",
            min_value=10,
            max_value=500,
            value=100
        )

    # ===== Apply sorting =====
    df_sorted = df.sort_values(
        by=sort_by,
        ascending=(ascending == "Ascending")
    )

    st.markdown("---")
    st.caption("Hasil data setelah sorting:")
    st.dataframe(
        df_sorted.head(n_rows),
        use_container_width=True,
        height=520
    )


# SUBPAGE: INSIGHT PARAM 
elif st.session_state.insight_subpage == "insight_param":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("Insight by Parameter (Coming soon)")
    st.info("Nanti di sini kita isi chart + filter parameter.")

else:
    go("home")
