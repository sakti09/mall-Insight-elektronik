import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="Insight", layout="wide")
st.title("Insight Dashboard — Data Understanding")

# =========================
# Helpers
# =========================
REQUIRED_COLS = [
    "gender", "age", "category", "quantity", "price",
    "payment_method", "shopping_mall",
    "invoice_date_time", "invoice_date_day", "invoice_date_month", "invoice_date_year",
    "total_spend", "age_class", "price_class",
]

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pastikan kolom inti tersedia. Kalau belum ada:
    - invoice_date_time -> parse
    - invoice_date_* -> extract
    - total_spend -> price * quantity
    """
    df = df.copy()

    # total_spend
    if "total_spend" not in df.columns and ("price" in df.columns and "quantity" in df.columns):
        df["total_spend"] = pd.to_numeric(df["price"], errors="coerce") * pd.to_numeric(df["quantity"], errors="coerce")

    # invoice_date_time
    if "invoice_date_time" in df.columns:
        df["invoice_date_time"] = pd.to_datetime(df["invoice_date_time"], errors="coerce")
    elif "invoice_date" in df.columns:
        df["invoice_date_time"] = pd.to_datetime(df["invoice_date"], dayfirst=True, errors="coerce")

    # invoice_date_day/month/year
    if "invoice_date_time" in df.columns and df["invoice_date_time"].notna().any():
        if "invoice_date_day" not in df.columns:
            df["invoice_date_day"] = df["invoice_date_time"].dt.day
        if "invoice_date_month" not in df.columns:
            df["invoice_date_month"] = df["invoice_date_time"].dt.month
        if "invoice_date_year" not in df.columns:
            df["invoice_date_year"] = df["invoice_date_time"].dt.year

    return df

def safe_multiselect(sidebar, label, series: pd.Series, default_all=True):
    opts = sorted([x for x in series.dropna().unique().tolist()])
    if not opts:
        sidebar.caption(f"{label} tidak tersedia.")
        return None
    default = opts if default_all else (opts[: min(10, len(opts))])
    return sidebar.multiselect(label, options=opts, default=default)

def agg_metric(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """
    Output selalu punya:
    - group_col
    - transaksi_count
    - total_spend_sum
    """
    out = (
        df.groupby(group_col, dropna=False)
          .agg(
              transaksi_count=("total_spend", "size"),
              total_spend_sum=("total_spend", "sum"),
              total_spend_avg=("total_spend", "mean"),
              price_avg=("price", "mean"),
              quantity_avg=("quantity", "mean"),
          )
          .reset_index()
    )
    return out

def plot_bar_and_pie(agg_df: pd.DataFrame, x_col: str, metric_col: str, title: str, top_n: int, sort_desc=True):
    """
    Render: bar + pie side-by-side
    """
    tmp = agg_df.copy()

    # sort & top_n (kalau top_n <= 0 => tampil semua)
    if sort_desc:
        tmp = tmp.sort_values(metric_col, ascending=False)
    if top_n and top_n > 0:
        tmp = tmp.head(top_n)

    left, right = st.columns(2)

    with left:
        fig = px.bar(tmp, x=x_col, y=metric_col, text=metric_col)
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(
            title=f"{title} — Bar",
            xaxis_title=x_col,
            yaxis_title=metric_col,
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.pie(tmp, names=x_col, values=metric_col, hole=0.35)
        fig.update_layout(
            title=f"{title} — Pie",
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================
# Load Data
# =========================
uploaded = st.file_uploader("Upload CSV (final insight)", type=["csv"])
if not uploaded:
    st.info("Upload CSV dulu untuk melihat dashboard insight.")
    st.stop()

df = pd.read_csv(uploaded)
df = ensure_columns(df)

# Quick validation info
missing_core = [c for c in REQUIRED_COLS if c not in df.columns]
if missing_core:
    st.warning(
        "Beberapa kolom inti tidak ditemukan:\n"
        f"- {missing_core}\n\n"
        "Dashboard tetap jalan (sebagian), tapi sebaiknya upload file `customer_shopping_data_final_insight.csv`."
    )

st.subheader("Preview Data")
st.dataframe(df.head(20), use_container_width=True)

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("Filters")

# Year / Month filters (paling penting)
if "invoice_date_year" in df.columns:
    years = sorted(df["invoice_date_year"].dropna().unique().tolist())
    sel_years = st.sidebar.multiselect("Year", years, default=years)
else:
    sel_years = None

if "invoice_date_month" in df.columns:
    months = list(range(1, 13))
    sel_months = st.sidebar.multiselect("Month", months, default=months)
else:
    sel_months = None

# Other filters
sel_genders = safe_multiselect(st.sidebar, "Gender", df["gender"]) if "gender" in df.columns else None
sel_cats = safe_multiselect(st.sidebar, "Category", df["category"], default_all=False) if "category" in df.columns else None
sel_malls = safe_multiselect(st.sidebar, "Shopping Mall", df["shopping_mall"], default_all=False) if "shopping_mall" in df.columns else None
sel_pay = safe_multiselect(st.sidebar, "Payment Method", df["payment_method"], default_all=True) if "payment_method" in df.columns else None

# Age range
if "age" in df.columns and df["age"].notna().any():
    min_age = int(df["age"].min())
    max_age = int(df["age"].max())
    age_range = st.sidebar.slider("Age range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
else:
    age_range = None

# Apply filters
mask = pd.Series(True, index=df.index)

if sel_years is not None and "invoice_date_year" in df.columns:
    mask &= df["invoice_date_year"].isin(sel_years)

if sel_months is not None and "invoice_date_month" in df.columns:
    mask &= df["invoice_date_month"].isin(sel_months)

if sel_genders is not None and "gender" in df.columns and len(sel_genders) > 0:
    mask &= df["gender"].isin(sel_genders)

if sel_cats is not None and "category" in df.columns and len(sel_cats) > 0:
    mask &= df["category"].isin(sel_cats)

if sel_malls is not None and "shopping_mall" in df.columns and len(sel_malls) > 0:
    mask &= df["shopping_mall"].isin(sel_malls)

if sel_pay is not None and "payment_method" in df.columns and len(sel_pay) > 0:
    mask &= df["payment_method"].isin(sel_pay)

if age_range is not None and "age" in df.columns:
    mask &= df["age"].between(age_range[0], age_range[1])

df_f = df[mask].copy()
st.caption(f"Filtered rows: {len(df_f):,} / {len(df):,}")

# =========================
# KPI Cards
# =========================
st.subheader("Key KPIs")

total_spend = float(df_f["total_spend"].sum()) if "total_spend" in df_f.columns else np.nan
avg_spend = float(df_f["total_spend"].mean()) if "total_spend" in df_f.columns else np.nan
total_qty = float(pd.to_numeric(df_f["quantity"], errors="coerce").sum()) if "quantity" in df_f.columns else np.nan
rows = len(df_f)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spend", "-" if np.isnan(total_spend) else f"{total_spend:,.0f}")
c2.metric("Avg Spend / Tx", "-" if np.isnan(avg_spend) else f"{avg_spend:,.0f}")
c3.metric("Total Quantity", "-" if np.isnan(total_qty) else f"{total_qty:,.0f}")
c4.metric("Transactions (Rows)", f"{rows:,.0f}")

# =========================
# Main Controls (Charts)
# =========================
st.subheader("Charts — Bar & Pie (Control)")

metric_choice = st.selectbox(
    "Pilih metric",
    ["Total Spend", "Jumlah Transaksi"],
    index=0
)

metric_col = "total_spend_sum" if metric_choice == "Total Spend" else "transaksi_count"

dim_options = []
if "gender" in df_f.columns: dim_options.append("gender")
if "age" in df_f.columns: dim_options.append("age")
if "age_class" in df_f.columns: dim_options.append("age_class")
if "category" in df_f.columns: dim_options.append("category")
if "shopping_mall" in df_f.columns: dim_options.append("shopping_mall")
if "payment_method" in df_f.columns: dim_options.append("payment_method")
if "invoice_date_year" in df_f.columns: dim_options.append("invoice_date_year")
if "invoice_date_month" in df_f.columns: dim_options.append("invoice_date_month")

dimension = st.selectbox(
    "Group by (dimensi)",
    dim_options,
    index=dim_options.index("category") if "category" in dim_options else 0
)

# Top-N: berguna untuk category/mall/age (age bisa banyak)
default_top = 10 if dimension in ["category", "shopping_mall"] else (20 if dimension == "age" else 0)
top_n = st.slider(
    "Top-N (0 = tampil semua)",
    min_value=0,
    max_value=50,
    value=min(default_top, 50),
    step=1
)

# Build aggregated dataframe
if len(df_f) == 0:
    st.info("Filter menghasilkan 0 baris, coba longgarkan filter.")
else:
    agg = agg_metric(df_f, dimension)

    title_map = {
        "gender": "Gender",
        "age": "Age",
        "age_class": "Age Class",
        "category": "Category",
        "shopping_mall": "Shopping Mall",
        "payment_method": "Payment Method",
        "invoice_date_year": "Year",
        "invoice_date_month": "Month",
    }
    title = f"{title_map.get(dimension, dimension)} vs {metric_choice}"

    # For month ordering
    order = None
    if dimension == "invoice_date_month":
        order = list(range(1, 13))
        # ensure present only
        present = agg[dimension].dropna().unique().tolist()
        order = [m for m in order if m in present]

    plot_bar_and_pie(
        agg_df=agg,
        x_col=dimension,
        metric_col=metric_col,
        title=title,
        top_n=top_n,
        sort_desc=True if dimension not in ["invoice_date_month", "age", "age_class", "invoice_date_year"] else False
    )

# =========================
# Quick Panels (recommended views)
# =========================
st.subheader("Quick Views (Recommended)")

tabs = st.tabs(["Gender", "Age Class", "Category", "Mall", "Payment", "Year", "Month"])

def quick_tab(group_col: str):
    if len(df_f) == 0 or group_col not in df_f.columns:
        st.info("Data tidak tersedia untuk tab ini.")
        return
    agg = agg_metric(df_f, group_col)

    # total spend view
    plot_bar_and_pie(
        agg_df=agg,
        x_col=group_col,
        metric_col="total_spend_sum",
        title=f"{group_col} vs Total Spend",
        top_n=10 if group_col in ["category", "shopping_mall"] else 0,
        sort_desc=True
    )

    # transaksi view
    plot_bar_and_pie(
        agg_df=agg,
        x_col=group_col,
        metric_col="transaksi_count",
        title=f"{group_col} vs Jumlah Transaksi",
        top_n=10 if group_col in ["category", "shopping_mall"] else 0,
        sort_desc=True
    )

with tabs[0]:
    quick_tab("gender")
with tabs[1]:
    quick_tab("age_class")
with tabs[2]:
    quick_tab("category")
with tabs[3]:
    quick_tab("shopping_mall")
with tabs[4]:
    quick_tab("payment_method")
with tabs[5]:
    quick_tab("invoice_date_year")
with tabs[6]:
    quick_tab("invoice_date_month")

# =========================
# Correlation Heatmap (Numeric)
# =========================
st.subheader("Correlation Heatmap (Numeric)")

num = df_f.select_dtypes(include="number")
if num.shape[1] >= 2:
    corr = num.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr.values)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    fig.colorbar(im, ax=ax)
    st.pyplot(fig, clear_figure=True)
else:
    st.info("Butuh minimal 2 kolom numerik untuk correlation heatmap.")
