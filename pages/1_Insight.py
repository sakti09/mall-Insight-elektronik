import streamlit as st
import pandas as pd

st.set_page_config(page_title="Insight", layout="wide")

#CSS
def inject_card_css():
    st.markdown(
        """
        <style>
        /* tombol streamlit jadi kartu */
        div.stButton > button {
            width: 100%;
            height: 90px;
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.08);
            background: linear-gradient(135deg, #16a34a, #22c55e);
            color: white;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            text-align: left;
            padding: 14px 16px;
            white-space: pre-line; /* biar \n jalan */
        }
        div.stButton > button:hover {
            filter: brightness(0.98);
            border-color: rgba(0,0,0,0.12);
        }
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

def card_button(label: str, emoji: str, key: str, on_click_page: str, disabled=False):
    btn_label = f"{emoji}  {label}\n\nKlik untuk buka"
    if st.button(btn_label, key=key, disabled=disabled, use_container_width=True):
        go(on_click_page)

# HOME (grid 10 kartu)
if st.session_state.insight_subpage == "home":
    st.subheader("Menu (Page 1)")
    st.caption("Klik kartu di bawah untuk membuka sub-halaman (masih di Page 1).")

    cols = st.columns(5)
    with cols[0]:
        card_button("1) View Dataset", "📄", "card_1", "view_dataset")
    with cols[1]:
        card_button("2) Insight by Parameter", "📊", "card_2", "insight_param")  # nanti kamu isi
    with cols[2]:
        card_button("3) Placeholder", "🧩", "card_3", "todo_3", disabled=True)
    with cols[3]:
        card_button("4) Placeholder", "🛍️", "card_4", "todo_4", disabled=True)
    with cols[4]:
        card_button("5) Placeholder", "💳", "card_5", "todo_5", disabled=True)

    cols2 = st.columns(5)
    with cols2[0]:
        card_button("6) Placeholder", "🗓️", "card_6", "todo_6", disabled=True)
    with cols2[1]:
        card_button("7) Placeholder", "🧠", "card_7", "todo_7", disabled=True)
    with cols2[2]:
        card_button("8) Placeholder", "📌", "card_8", "todo_8", disabled=True)
    with cols2[3]:
        card_button("9) Placeholder", "📈", "card_9", "todo_9", disabled=True)
    with cols2[4]:
        card_button("10) Placeholder", "⚙️", "card_10", "todo_10", disabled=True)

    st.markdown("---")
    st.write("Preview cepat dataset (top 5):")
    st.dataframe(df.head(5), use_container_width=True)

# SUBPAGE: VIEW DATASET
elif st.session_state.insight_subpage == "view_dataset":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("⬅️ Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("View Dataset")

    st.caption("Bagian 1: tampilkan 10 baris pertama (scrollable).")
    st.dataframe(df.head(10), use_container_width=True, height=260)

    st.markdown("---")

    st.caption("Bagian 2: tabel yang bisa kamu urutkan (sorting).")
    st.write("Cara 1: klik header kolom di tabel (biasanya bisa sort naik/turun).")
    st.dataframe(df, use_container_width=True, height=360)

    st.markdown("**Cara 2 (kontrol sorting):** pilih kolom & urutan, lalu tampilkan hasil sort.")
    sort_cols = df.columns.tolist()
    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        default_idx = sort_cols.index("age") if "age" in sort_cols else 0
        sort_by = st.selectbox("Sort by column", options=sort_cols, index=default_idx)
    with c2:
        ascending = st.radio("Order", options=["Ascending", "Descending"], horizontal=True)
    with c3:
        n_rows = st.slider("Tampilkan berapa baris hasil sort?", 10, 200, 50)

    df_sorted = df.sort_values(by=sort_by, ascending=(ascending == "Ascending"))
    st.dataframe(df_sorted.head(n_rows), use_container_width=True, height=360)


# SUBPAGE: INSIGHT PARAM 
elif st.session_state.insight_subpage == "insight_param":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("⬅️ Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("Insight by Parameter (Coming soon)")
    st.info("Nanti di sini kita isi chart + filter parameter.")

else:
    go("home")
