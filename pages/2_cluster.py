import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Cluster", layout="wide")


# LOAD CSS (pakai insight.css)
def load_css(path: str = "assets/insight.css"):
    css_path = Path(path)
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

load_css()

st.title("Page 2 — Cluster Dashboard")
st.caption("Visualisasi hasil clustering dari CSV (best model).")

# HELPERS
def pick_col(df, candidates):
    """Return first existing column name from candidates (case-insensitive)."""
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None

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
        <div class="kpi-wrap">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def ensure_numeric(s: pd.Series):
    return pd.to_numeric(s, errors="coerce")

def safe_value_counts(s: pd.Series):
    return s.astype(str).fillna("NaN").value_counts()


# LOAD DATA (A: repo file OR B: uploader)
st.sidebar.header("Data Source")

default_path = st.sidebar.text_input(
    "Path CSV di repo (opsional)",
    value="assets/cluster_best.csv",
    help="Kalau kamu taruh CSV cluster di repo, isi path-nya di sini. Contoh: assets/cluster_best.csv"
)

use_repo_file = st.sidebar.checkbox("Pakai file dari repo (kalau ada)", value=True)

df = None
if use_repo_file and Path(default_path).exists():
    df = pd.read_csv(default_path)
    st.success(f"Loaded dari repo: {default_path}")
else:
    uploaded = st.file_uploader("Upload CSV hasil cluster", type=["csv"])
    if not uploaded:
        st.info("Upload CSV cluster dulu atau taruh file-nya di repo dan centang 'Pakai file dari repo'.")
        st.stop()
    df = pd.read_csv(uploaded)


# DETECT IMPORTANT COLUMNS
cluster_col = pick_col(df, ["cluster", "cluster_label", "cluster_id", "label", "kelas", "class"])
spend_col   = pick_col(df, ["total_spend", "total", "spend", "amount", "revenue", "sales"])
age_col     = pick_col(df, ["age", "umur"])
cat_col     = pick_col(df, ["category", "kategori"])
gender_col  = pick_col(df, ["gender", "sex"])
pay_col     = pick_col(df, ["payment_method", "payment", "pay"])
mall_col    = pick_col(df, ["shopping_mall", "mall"])
qty_col     = pick_col(df, ["quantity", "qty"])
price_col   = pick_col(df, ["price", "unit_price"])

if cluster_col is None:
    st.error("Kolom cluster tidak ditemukan. Pastikan CSV punya kolom seperti: cluster / cluster_label / cluster_id.")
    st.stop()

# normalisasi tipe cluster biar rapi
df[cluster_col] = df[cluster_col].astype(str)

# numeric columns (auto)
numeric_cols = df.select_dtypes(include="number").columns.tolist()


# SIDEBAR FILTERS
st.sidebar.header("Filters")

clusters = sorted(df[cluster_col].dropna().unique().tolist())
selected_clusters = st.sidebar.multiselect("Cluster", options=clusters, default=clusters)

df_f = df.copy()
if selected_clusters:
    df_f = df_f[df_f[cluster_col].isin(selected_clusters)]

# optional filters
if cat_col is not None:
    cats = sorted(df_f[cat_col].dropna().astype(str).unique().tolist())
    selected_cats = st.sidebar.multiselect("Category", options=cats, default=cats)
    if selected_cats:
        df_f = df_f[df_f[cat_col].astype(str).isin(selected_cats)]

if gender_col is not None:
    genders = sorted(df_f[gender_col].dropna().astype(str).unique().tolist())
    selected_gender = st.sidebar.multiselect("Gender", options=genders, default=genders)
    if selected_gender:
        df_f = df_f[df_f[gender_col].astype(str).isin(selected_gender)]

st.sidebar.caption(f"Filtered rows: {len(df_f):,} / {len(df):,}")

#PREVIEW
with st.expander("Preview data (head)", expanded=False):
    st.dataframe(df_f.head(30), use_container_width=True)

#kpi
st.subheader("Ringkasan")
c1, c2, c3, c4 = st.columns(4)

with c1:
    render_kpi("Rows", fmt_int(len(df_f)))
with c2:
    render_kpi("Jumlah Cluster Terpilih", fmt_int(len(selected_clusters)))
with c3:
    if spend_col is not None:
        render_kpi("Total Spend", fmt_money(ensure_numeric(df_f[spend_col]).sum()))
    else:
        render_kpi("Total Spend", "-", "kolom total_spend tidak ada")
with c4:
    if spend_col is not None:
        render_kpi("Avg Spend", fmt_money(ensure_numeric(df_f[spend_col]).mean()))
    else:
        render_kpi("Avg Spend", "-")

# CHARTS - CLUSTER OVERVIEW
st.subheader("Cluster Overview")

left, right = st.columns(2)

# 1) Count per cluster
with left:
    st.markdown("**Jumlah Data per Cluster**")
    vc = safe_value_counts(df_f[cluster_col]).reset_index()
    vc.columns = [cluster_col, "count"]
    fig = px.bar(vc, x=cluster_col, y="count", hover_data=["count"], title="Count per Cluster")
    st.plotly_chart(fig, use_container_width=True, key="cluster_count_bar")

# 2) Total spend per cluster
with right:
    st.markdown("**Total Spend per Cluster**")
    if spend_col is None:
        st.info("Kolom total_spend tidak ada di CSV.")
    else:
        grp = (
            df_f.groupby(cluster_col)[spend_col]
            .sum()
            .reset_index()
            .sort_values(spend_col, ascending=False)
        )
        fig = px.bar(grp, x=cluster_col, y=spend_col, hover_data=[spend_col], title="Total Spend per Cluster")
        st.plotly_chart(fig, use_container_width=True, key="cluster_spend_bar")

# 3) Boxplot spend per cluster
st.markdown("**Sebaran Spend per Cluster (Boxplot)**")
if spend_col is None:
    st.info("Kolom total_spend tidak ada.")
else:
    tmp = df_f.copy()
    tmp[spend_col] = ensure_numeric(tmp[spend_col])
    tmp = tmp.dropna(subset=[spend_col])
    fig = px.box(tmp, x=cluster_col, y=spend_col, points="outliers", title="Distribusi Spend per Cluster (Boxplot)")
    st.plotly_chart(fig, use_container_width=True, key="cluster_spend_box")

# HEATMAP NUMERIC MEANS PER CLUSTER
st.subheader("Profil Cluster (Rata-rata Fitur Numerik)")
if len(numeric_cols) == 0:
    st.info("Tidak ada kolom numerik untuk heatmap.")
else:
    # pilih numeric columns (exclude year/month/day kalau mau)
    exclude_like = {"invoice_date_day", "invoice_date_month", "invoice_date_year"}
    numeric_cols_use = [c for c in numeric_cols if c not in exclude_like]

    cols_pick = st.multiselect(
        "Pilih fitur numerik untuk heatmap",
        options=numeric_cols_use,
        default=numeric_cols_use[: min(8, len(numeric_cols_use))],
    )

    if cols_pick:
        prof = df_f.groupby(cluster_col)[cols_pick].mean(numeric_only=True)
        fig = px.imshow(
            prof,
            aspect="auto",
            title="Mean Numeric Features per Cluster (Heatmap)",
        )
        st.plotly_chart(fig, use_container_width=True, key="cluster_heatmap")
    else:
        st.info("Pilih minimal 1 kolom numerik untuk heatmap.")

# CATEGORY MIX (stacked bar)
st.subheader("Komposisi Kategori per Cluster")
if cat_col is None:
    st.info("Kolom category tidak ada di CSV.")
else:
    topk = st.slider("Tampilkan Top K kategori", 5, 20, 10)
    # ambil kategori paling sering agar chart tidak terlalu ramai
    top_cats = df_f[cat_col].astype(str).value_counts().head(topk).index.tolist()
    df_cat = df_f[df_f[cat_col].astype(str).isin(top_cats)].copy()

    ct = (
        df_cat.groupby([cluster_col, cat_col])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        ct,
        x=cluster_col,
        y="count",
        color=cat_col,
        title=f"Top {topk} Category Mix per Cluster (Count)",
        hover_data=["count"],
    )
    fig.update_layout(barmode="stack")
    st.plotly_chart(fig, use_container_width=True, key="cluster_cat_stack")


#2D SCATTER IF EMBEDDING EXISTS
st.subheader("Scatter 2D (opsional)")
x2 = pick_col(df_f, ["pc1", "pca1", "tsne1", "umap1", "x1", "dim1"])
y2 = pick_col(df_f, ["pc2", "pca2", "tsne2", "umap2", "x2", "dim2"])

if x2 and y2:
    st.caption(f"Terbaca kolom embedding: {x2} vs {y2}")
    hover_cols = [c for c in [spend_col, age_col, cat_col, gender_col, pay_col, mall_col] if c is not None]
    fig = px.scatter(
        df_f,
        x=x2,
        y=y2,
        color=cluster_col,
        hover_data=hover_cols,
        title="Scatter 2D (Embedding/PCA/t-SNE/UMAP)",
        opacity=0.75
    )
    st.plotly_chart(fig, use_container_width=True, key="cluster_scatter_2d")
else:
    st.info("Tidak menemukan kolom embedding 2D (pc1/pc2, pca1/pca2, tsne1/tsne2, umap1/umap2). Kalau ada, scatter akan muncul otomatis.")

st.markdown("---")
st.caption("Tip: kalau kamu mau, kita bisa buat juga 'Cluster Persona' per cluster (Top category, top mall, avg spend, dll).")
