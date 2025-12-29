import streamlit as st
import pandas as pd

st.set_page_config(page_title="Insight", layout="wide")

# Load data
uploaded = st.file_uploader("Upload CSV (final insight)", type=["csv"])
if not uploaded:
    st.info("Upload CSV dulu untuk melihat dashboard insight.")
    st.stop()

df = pd.read_csv(uploaded)

st.title("Page 1 — Insight Dashboard")

# Simple subpage router (inside Page 1)
if "insight_subpage" not in st.session_state:
    st.session_state.insight_subpage = "home"

def go(page_name: str):
    st.session_state.insight_subpage = page_name


# UI: green clickable cards
def card_button(label: str, emoji: str, key: str, on_click_page: str, disabled=False):
    """
    Green card-like button using HTML + st.button overlay.
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #16a34a, #22c55e);
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 16px;
            padding: 16px 14px;
            height: 90px;
            color: white;
            display:flex;
            align-items:center;
            justify-content:space-between;
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        ">
            <div style="display:flex; flex-direction:column; gap:6px;">
                <div style="font-size:14px; opacity:0.95;">{label}</div>
                <div style="font-size:11px; opacity:0.85;">Klik untuk buka</div>
            </div>
            <div style="font-size:28px;">{emoji}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # tombol transparan di bawah kartu (biar bisa diklik)
    clicked = st.button("Open", key=key, disabled=disabled, use_container_width=True)
    if clicked:
        go(on_click_page)

# HOME (grid of 10 icons)
if st.session_state.insight_subpage == "home":
    st.subheader("Menu (Page 1)")
    st.caption("Klik kartu di bawah untuk membuka sub-halaman (masih di Page 1).")

    # 10 cards (icon 1 aktif, sisanya placeholder)
    cols = st.columns(5)
    with cols[0]:
        card_button("1) View Dataset", "📄", "card_1", "view_dataset")
    with cols[1]:
        card_button("2) Placeholder", "📊", "card_2", "todo_2", disabled=True)
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
        sort_by = st.selectbox("Sort by column", options=sort_cols, index=sort_cols.index("age") if "age" in sort_cols else 0)
    with c2:
        ascending = st.radio("Order", options=["Ascending", "Descending"], horizontal=True)
    with c3:
        n_rows = st.slider("Tampilkan berapa baris hasil sort?", 10, 200, 50)

    df_sorted = df.sort_values(by=sort_by, ascending=(ascending == "Ascending"))
    st.dataframe(df_sorted.head(n_rows), use_container_width=True, height=360)

else:
    # fallback
    go("home")
