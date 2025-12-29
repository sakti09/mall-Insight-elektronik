import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Cluster", layout="wide")

# load css khusus cluster
def load_css(css_path: str):
    p = Path(css_path)
    if p.exists():
        st.markdown(
            f"<style>{p.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True
        )

load_css("assets/insight.css")

st.title("Cluster Dashboard")
st.caption("Visualisasi hasil clustering Fuzzy C-Means (best model) dan insight bisnis berbasis mall.")

# -------------------------
# helper functions
# -------------------------
def pick_col(df, candidates):
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None

def ensure_numeric(s: pd.Series):
    return pd.to_numeric(s, errors="coerce")

def fmt_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return "-"

def fmt_money(x):
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return "-"

def render_kpi(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="kpi-cluster">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def safe_value_counts(s: pd.Series):
    return s.astype(str).fillna("NaN").value_counts()

# -------------------------
# sidebar — data source
# -------------------------
st.sidebar.header("Data Source")

default_path = st.sidebar.text_input(
    "Path CSV hasil clustering",
    value="assets/customer_fcm_best_model.csv",
    help="Contoh: assets/customer_fcm_best_model.csv"
)

use_repo_file = st.sidebar.checkbox("Pakai file dari repo", value=True)

df = None
if use_repo_file and Path(default_path).exists():
    df = pd.read_csv(default_path)
    st.sidebar.success(f"Loaded: {default_path}")
else:
    uploaded = st.sidebar.file_uploader("Upload CSV hasil cluster", type=["csv"])
    if not uploaded:
        st.info("Upload CSV hasil clustering atau simpan file di repo.")
        st.stop()
    df = pd.read_csv(uploaded)
    st.sidebar.success("Loaded: uploaded CSV")

# -------------------------
# detect important columns
# -------------------------
cluster_col = pick_col(df, ["cluster", "cluster_label", "class"])
age_col     = pick_col(df, ["age", "umur"])
qty_col     = pick_col(df, ["quantity", "qty"])
price_col   = pick_col(df, ["price"])
spend_col   = pick_col(df, ["total_spent", "total_spend", "spend", "amount"])
cat_col     = pick_col(df, ["category", "kategori"])
gender_col  = pick_col(df, ["gender"])
pay_col     = pick_col(df, ["payment_method", "payment"])
mall_col    = pick_col(df, ["shopping_mall", "mall"])

if cluster_col is None:
    st.error("Kolom cluster tidak ditemukan di CSV.")
    st.stop()

df[cluster_col] = df[cluster_col].astype(str)

# -------------------------
# sidebar — filters
# -------------------------
st.sidebar.header("Filters")

clusters = sorted(df[cluster_col].unique().tolist())
selected_clusters = st.sidebar.multiselect(
    "Cluster",
    options=clusters,
    default=clusters
)

df_f = df.copy()
if selected_clusters:
    df_f = df_f[df_f[cluster_col].isin(selected_clusters)]

if cat_col is not None:
    cats = sorted(df_f[cat_col].astype(str).unique().tolist())
    selected_cats = st.sidebar.multiselect("Category", cats, cats)
    df_f = df_f[df_f[cat_col].astype(str).isin(selected_cats)]

if gender_col is not None:
    genders = sorted(df_f[gender_col].astype(str).unique().tolist())
    selected_gender = st.sidebar.multiselect("Gender", genders, genders)
    df_f = df_f[df_f[gender_col].astype(str).isin(selected_gender)]

if mall_col is not None:
    malls = sorted(df_f[mall_col].astype(str).unique().tolist())
    selected_malls = st.sidebar.multiselect("Shopping Mall", malls, malls)
    df_f = df_f[df_f[mall_col].astype(str).isin(selected_malls)]

st.sidebar.caption(f"Filtered rows: {len(df_f):,} / {len(df):,}")

# -------------------------
# preview
# -------------------------
with st.expander("Preview data (head)", expanded=False):
    st.dataframe(df_f.head(25), use_container_width=True)

# -------------------------
# KPI section
# -------------------------
st.subheader("Ringkasan")

k1, k2, k3, k4 = st.columns(4)

with k1:
    render_kpi("Jumlah Data", fmt_int(len(df_f)))

with k2:
    render_kpi("Jumlah Cluster", fmt_int(len(selected_clusters)))

with k3:
    if spend_col:
        render_kpi("Total Spend", fmt_money(ensure_numeric(df_f[spend_col]).sum()))
    else:
        render_kpi("Total Spend", "-")

with k4:
    if spend_col:
        render_kpi("Rata-rata Spend", fmt_money(ensure_numeric(df_f[spend_col]).mean()))
    else:
        render_kpi("Rata-rata Spend", "-")

st.markdown("---")

# -------------------------
# cluster overview
# -------------------------
st.subheader("Cluster Overview")

c_left, c_right = st.columns(2)

with c_left:
    vc = safe_value_counts(df_f[cluster_col]).reset_index()
    vc.columns = [cluster_col, "count"]
    fig = px.bar(vc, x=cluster_col, y="count", title="Jumlah Data per Cluster")
    st.plotly_chart(fig, use_container_width=True)

with c_right:
    if spend_col:
        grp = (
            df_f.groupby(cluster_col)[spend_col]
            .sum()
            .reset_index()
            .sort_values(spend_col, ascending=False)
        )
        fig = px.bar(grp, x=cluster_col, y=spend_col, title="Total Spend per Cluster")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# mall insight
# -------------------------
st.markdown("---")
st.subheader("Mall Insight")

if mall_col:
    focus_mall = st.selectbox(
        "Pilih mall fokus",
        sorted(df_f[mall_col].astype(str).unique().tolist()),
    )

    mall_df = df_f[df_f[mall_col].astype(str) == str(focus_mall)]

    if len(mall_df) > 0:
        a, b, c = st.columns(3)
        with a:
            render_kpi("Jumlah Transaksi", fmt_int(len(mall_df)))
        with b:
            if spend_col:
                render_kpi("Avg Spend", fmt_money(ensure_numeric(mall_df[spend_col]).mean()))
        with c:
            render_kpi("Cluster Dominan", safe_value_counts(mall_df[cluster_col]).idxmax())

        mall_counts = safe_value_counts(mall_df[cluster_col]).reset_index()
        mall_counts.columns = [cluster_col, "count"]
        fig = px.bar(mall_counts, x=cluster_col, y="count",
                     title=f"Distribusi Cluster di {focus_mall}")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Rekomendasi Strategi Bisnis", expanded=True):
            st.markdown(
                """
                <div class="insight-cluster">
                    <div class="insight-title">Tujuan</div>
                    <div class="insight-text">
                        Meningkatkan nilai belanja per transaksi pada mall dengan volume kunjungan tinggi,
                        khususnya dari segmen pelanggan low dan medium spender.
                    </div>
                    <div class="insight-title">Strategi yang Disarankan</div>
                    <ul class="insight-list">
                        <li>Bundling produk lintas kategori (contoh: Clothing + Shoes).</li>
                        <li>Promosi berbasis kuantitas seperti beli 2 gratis 1.</li>
                        <li>Diskon bertingkat berdasarkan total belanja.</li>
                        <li>Cross-selling produk pelengkap di kasir.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")
st.caption("Data sumber: customer_fcm_best_model.csv")
