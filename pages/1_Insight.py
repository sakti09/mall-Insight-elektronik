import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(page_title="Insight", layout="wide")
st.title("Insight Dashboard")

# ---------- Helpers ----------
def pick_col(df, candidates):
    """Return first existing column name from candidates (case-insensitive)."""
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None

def coerce_datetime(s: pd.Series):
    return pd.to_datetime(s, errors="coerce", utc=False)

# ---------- Load Data ----------
uploaded = st.file_uploader("Upload file CSV", type=["csv"])

if not uploaded:
    st.info("Upload CSV dulu untuk melihat dashboard insight.")
    st.stop()

df = pd.read_csv(uploaded)

# Try to detect common columns
date_col = pick_col(df, ["invoice_date", "date", "order_date", "transaction_date", "invoice_datetime"])
category_col = pick_col(df, ["category", "product_category", "item_category", "class", "price_class"])
gender_col = pick_col(df, ["gender", "sex"])
spend_col = pick_col(df, ["total_spend", "total", "spend", "revenue", "amount", "sales"])
qty_col = pick_col(df, ["quantity", "qty", "items"])
price_col = pick_col(df, ["price", "unit_price"])

# If total_spend not present, try to create it from price * quantity
if spend_col is None and (price_col is not None and qty_col is not None):
    df["total_spend"] = pd.to_numeric(df[price_col], errors="coerce") * pd.to_numeric(df[qty_col], errors="coerce")
    spend_col = "total_spend"

# Parse date if present
if date_col is not None:
    df[date_col] = coerce_datetime(df[date_col])

st.subheader("Preview Data")
st.dataframe(df.head(20), use_container_width=True)

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")

# Date filter
if date_col is not None and df[date_col].notna().any():
    min_d = df[date_col].min().date()
    max_d = df[date_col].max().date()
    start_d, end_d = st.sidebar.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    if isinstance(start_d, tuple) or isinstance(start_d, list):
        # in case Streamlit returns tuple for older behavior
        start_d, end_d = start_d
    mask_date = df[date_col].dt.date.between(start_d, end_d)
else:
    st.sidebar.caption("Date column not found → date filter disabled")
    mask_date = pd.Series([True] * len(df))

# Category filter
if category_col is not None:
    cats = sorted([c for c in df[category_col].dropna().unique().tolist()])
    selected_cats = st.sidebar.multiselect("Category", options=cats, default=cats[: min(10, len(cats))] if len(cats) else [])
    if selected_cats:
        mask_cat = df[category_col].isin(selected_cats)
    else:
        mask_cat = pd.Series([True] * len(df))
else:
    st.sidebar.caption("Category column not found → category filter disabled")
    mask_cat = pd.Series([True] * len(df))

# Gender filter
if gender_col is not None:
    genders = sorted([g for g in df[gender_col].dropna().unique().tolist()])
    selected_genders = st.sidebar.multiselect("Gender", options=genders, default=genders)
    if selected_genders:
        mask_gender = df[gender_col].isin(selected_genders)
    else:
        mask_gender = pd.Series([True] * len(df))
else:
    st.sidebar.caption("Gender column not found → gender filter disabled")
    mask_gender = pd.Series([True] * len(df))

df_f = df[mask_date & mask_cat & mask_gender].copy()

st.caption(f"Filtered rows: {len(df_f):,} / {len(df):,}")

# ---------- KPI Cards ----------
st.subheader("Key KPIs")

total_spend = float(df_f[spend_col].sum()) if spend_col is not None else np.nan
avg_order = float(df_f[spend_col].mean()) if spend_col is not None else np.nan
total_qty = float(pd.to_numeric(df_f[qty_col], errors="coerce").sum()) if qty_col is not None else np.nan

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Spend", "-" if np.isnan(total_spend) else f"{total_spend:,.0f}")
c2.metric("Avg Spend / Row", "-" if np.isnan(avg_order) else f"{avg_order:,.0f}")
c3.metric("Total Quantity", "-" if np.isnan(total_qty) else f"{total_qty:,.0f}")
c4.metric("Rows", f"{len(df_f):,}")

if spend_col is None:
    st.warning("Kolom total spend tidak ditemukan. Tambahkan kolom `total_spend` atau pastikan ada `price` + `quantity`.")

# ---------- Charts ----------
st.subheader("Charts")
left, right = st.columns(2)

# Bar: spend by category
with left:
    st.markdown("**Spend by Category (Bar)**")
    if spend_col is not None and category_col is not None and len(df_f) > 0:
        grp = df_f.groupby(category_col, dropna=False)[spend_col].sum().sort_values(ascending=False).head(20).reset_index()
        fig = px.bar(grp, x=category_col, y=spend_col)
        fig.update_layout(xaxis_title="Category", yaxis_title="Total Spend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Butuh kolom spend + category untuk bar chart.")

# Line: spend over time
with right:
    st.markdown("**Spend Over Time (Line)**")
    if spend_col is not None and date_col is not None and df_f[date_col].notna().any():
        tmp = df_f.dropna(subset=[date_col]).copy()
        tmp["date_day"] = tmp[date_col].dt.date
        ts = tmp.groupby("date_day")[spend_col].sum().reset_index()
        fig = px.line(ts, x="date_day", y=spend_col)
        fig.update_layout(xaxis_title="Date", yaxis_title="Total Spend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Butuh kolom spend + date untuk line chart.")

# Heatmap: correlation
st.markdown("**Correlation Heatmap (Numeric)**")
num = df_f.select_dtypes(include="number")
if num.shape[1] >= 2:
    corr = num.corr(numeric_only=True)

    fig, ax = plt.subplots()
    im = ax.imshow(corr.values)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha="right")
    ax.set_yticklabels(corr.columns)
    fig.colorbar(im, ax=ax)
    st.pyplot(fig, clear_figure=True)
else:
    st.info("Butuh minimal 2 kolom numerik untuk correlation heatmap.")
