import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Insight", layout="wide")

# =========================
# CSS (UI Styling)
# =========================
def inject_css():
    st.markdown(
        """
        <style>
        .stApp { background-color: #ffffff; }
        h1, h2, h3 { color: #1F3020; }
        .stCaption { color: rgba(31,48,32,0.75); }

        /* Dataframe styling */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            padding: 8px;
            background-color: #FAFAFA;
        }

        /* Card button base */
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

        /* Card color variants */
        .card-1 button { background: linear-gradient(135deg, #3A4A3B, #1F3020) !important; }
        .card-2 button { background: linear-gradient(135deg, #698A6B, #3A4A3B) !important; }
        .card-3 button { background: linear-gradient(135deg, #A9C2AA, #698A6B) !important; color:#0F1C10 !important; }
        .card-4 button { background: linear-gradient(135deg, #1F3020, #0F1C10) !important; }
        .card-5 button { background: linear-gradient(135deg, #0F1C10, #3A4A3B) !important; }

        /* Pretty tables */
        .note-wrap {
            background: #F6FAF6;
            border: 1px solid #E3EEE4;
            border-radius: 14px;
            padding: 14px 14px 6px 14px;
        }
        table.pretty {
            width: 100%;
            border-collapse: collapse;
            overflow: hidden;
            border-radius: 12px;
            margin: 10px 0 14px 0;
        }
        table.pretty thead th {
            background: linear-gradient(135deg, #1F3020, #3A4A3B);
            color: #ffffff;
            padding: 10px 12px;
            font-weight: 700;
            font-size: 13px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.15);
        }
        table.pretty tbody td {
            padding: 10px 12px;
            border-bottom: 1px solid #E6EFE7;
            font-size: 13px;
            color: #0F1C10;
        }
        table.pretty tbody tr:nth-child(odd) { background: #FFFFFF; }
        table.pretty tbody tr:nth-child(even) { background: #EEF6EF; }
        .pill {
            display:inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            background: #DDECDD;
            border: 1px solid #CBE0CC;
            font-size: 12px;
            font-weight: 700;
            color: #1F3020;
        }

        /* KPI cards */
        .kpi-wrap {
            background: #F6FAF6;
            border: 1px solid #E3EEE4;
            border-radius: 14px;
            padding: 12px 14px;
        }
        .kpi-title { color:#1F3020; font-weight:800; font-size:12px; opacity:0.9; }
        .kpi-value { color:#0F1C10; font-weight:900; font-size:24px; margin-top:2px; }
        .kpi-sub { color:#4B6650; font-size:12px; margin-top:2px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

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
# Router subpage
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
# Bottom notes: preprocessing mappings
# =========================
def show_preprocessing_notes():
    ageclass_desc = {
        1: "≤ 20 tahun",
        2: "21 – 30 tahun",
        3: "31 – 40 tahun",
        4: "41 – 50 tahun",
        5: "51 – 60 tahun",
        6: "61 – 70 tahun"
    }

    price_class_desc = {
        0: "price ≤ 20",
        1: "20 < price ≤ 50",
        2: "50 < price ≤ 100",
        3: "100 < price ≤ 500",
        4: "500 < price ≤ 1000",
        5: "1000 < price ≤ 2000",
        6: "price > 2000"
    }

    st.markdown("---")
    st.subheader("Keterangan Kolom Hasil Preprocessing")
    st.caption("Dokumentasi mapping fitur buatan (age_class & price_class).")

    age_rows = "".join(
        [f"<tr><td><span class='pill'>{k}</span></td><td>{v}</td></tr>" for k, v in ageclass_desc.items()]
    )
    age_table_html = f"""
    <div class="note-wrap">
      <h4 style="margin: 4px 0 10px 0; color:#1F3020;">Age Class (age_class)</h4>
      <table class="pretty">
        <thead>
          <tr>
            <th style="width:160px;">age_class</th>
            <th>Rentang usia</th>
          </tr>
        </thead>
        <tbody>
          {age_rows}
        </tbody>
      </table>
    </div>
    """
    st.markdown(age_table_html, unsafe_allow_html=True)

    price_rows = "".join(
        [f"<tr><td><span class='pill'>{k}</span></td><td>{v}</td></tr>" for k, v in price_class_desc.items()]
    )
    price_table_html = f"""
    <div class="note-wrap" style="margin-top:14px;">
      <h4 style="margin: 4px 0 10px 0; color:#1F3020;">Price Class (price_class)</h4>
      <table class="pretty">
        <thead>
          <tr>
            <th style="width:160px;">price_class</th>
            <th>Rentang harga (price)</th>
          </tr>
        </thead>
        <tbody>
          {price_rows}
        </tbody>
      </table>
      <div style="font-size:12px; color:#4B6650; margin-top:6px;">
        Catatan: <i>price_class dibuat untuk mengelompokkan harga agar analisis lebih ringkas.</i>
      </div>
    </div>
    """
    st.markdown(price_table_html, unsafe_allow_html=True)

# =========================
# Helpers: KPI & Insight table
# =========================
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

def insight_by(df_in: pd.DataFrame, group_col: str):
    out = (
        df_in.groupby(group_col, dropna=False)
        .agg(
            transaksi_count=("total_spend", "size"),
            total_spend_sum=("total_spend", "sum"),
            total_spend_avg=("total_spend", "mean"),
        )
        .reset_index()
    )
    return out

def smart_xtick_rotation(values) -> int:
    """Auto rotate if labels are long or too many."""
    try:
        vals = [str(v) for v in values]
        maxlen = max(len(v) for v in vals) if vals else 0
        n = len(vals)
        if maxlen >= 12 or n >= 8:
            return 45
        return 0
    except Exception:
        return 0

# =========================
# HOME
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
    show_preprocessing_notes()

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
    show_preprocessing_notes()

# =========================
# SUBPAGE: INSIGHT PARAMETER (BAR + PIE + CONTROLS)
# =========================
elif st.session_state.insight_subpage == "insight_param":
    topbar = st.columns([1, 6])
    with topbar[0]:
        if st.button("⬅️ Back", use_container_width=True):
            go("home")
    with topbar[1]:
        st.subheader("Insight by Parameter")
        st.caption("Chart interaktif (hover detail). Ada sorting, Top N vs All, & pie metric.")

    if "total_spend" not in df.columns:
        st.error("Kolom `total_spend` tidak ditemukan. Pastikan dataset final punya kolom total_spend.")
        st.stop()

    # Excluded from controls
    excluded_controls = {"age", "invoice_date_time", "invoice_date_day", "invoice_date_month", "invoice_date_year"}

    # Allowed controls (only if exist)
    controls = [
        "gender",
        "category",
        "quantity",
        "payment_method",
        "shopping_mall",
        "age_class",
        "price_class",
        "price",
    ]
    controls = [c for c in controls if c in df.columns and c not in excluded_controls]

    left, right = st.columns([3, 1])

    with right:
        st.markdown("### Filter Parameter")
        st.caption("Kosongkan (default semua) untuk melihat keseluruhan.")

        filter_state = {}
        for col in controls:
            if pd.api.types.is_numeric_dtype(df[col]):
                col_min = float(pd.to_numeric(df[col], errors="coerce").min())
                col_max = float(pd.to_numeric(df[col], errors="coerce").max())
                if col_min == col_max:
                    filter_state[col] = (col_min, col_max)
                    st.caption(f"{col}: hanya 1 nilai ({col_min})")
                else:
                    filter_state[col] = st.slider(
                        f"{col} (range)",
                        min_value=col_min,
                        max_value=col_max,
                        value=(col_min, col_max),
                    )
            else:
                opts = sorted(df[col].dropna().astype(str).unique().tolist())
                chosen = st.multiselect(col, options=opts, default=opts)
                filter_state[col] = chosen

        st.markdown("---")
        group_by_options = [c for c in ["gender", "category", "payment_method", "shopping_mall", "age_class", "price_class", "quantity", "price"] if c in df.columns]
        group_by = st.selectbox("Group by", options=group_by_options, index=0)

        sort_metric = st.radio(
            "Sort by",
            options=["Total Spend", "Jumlah Transaksi"],
            horizontal=True
        )

        top_mode = st.radio(
            "Tampilkan",
            options=["Top N", "All"],
            horizontal=True
        )

        top_n = st.slider("Top N", 5, 30, 10, disabled=(top_mode == "All"))

        pie_metric = st.radio(
            "Pie berdasarkan",
            options=["Total Spend", "Jumlah Transaksi"],
            horizontal=True
        )

    # Apply filters
    df_f = df.copy()
    for col, sel in filter_state.items():
        if pd.api.types.is_numeric_dtype(df_f[col]):
            lo, hi = sel
            df_f = df_f[pd.to_numeric(df_f[col], errors="coerce").between(lo, hi)]
        else:
            if sel:
                df_f = df_f[df_f[col].astype(str).isin(sel)]

    with left:
        st.markdown("### Ringkasan (hasil filter)")

        total_trx = len(df_f)
        total_spend = float(pd.to_numeric(df_f["total_spend"], errors="coerce").sum())
        avg_spend = float(pd.to_numeric(df_f["total_spend"], errors="coerce").mean()) if total_trx > 0 else 0.0

        k1, k2, k3 = st.columns(3)
        with k1:
            render_kpi("Jumlah Transaksi", fmt_int(total_trx), "jumlah baris setelah filter")
        with k2:
            render_kpi("Total Spend", fmt_money(total_spend), "sum(total_spend)")
        with k3:
            render_kpi("Rata-rata Spend", fmt_money(avg_spend), "mean(total_spend)")

        st.markdown("---")

        if total_trx == 0:
            st.warning("Data kosong setelah filter. Coba longgarkan filter.")
        else:
            insight = insight_by(df_f, group_by)

            # sort
            if sort_metric == "Jumlah Transaksi":
                insight = insight.sort_values("transaksi_count", ascending=False)
            else:
                insight = insight.sort_values("total_spend_sum", ascending=False)

            # Top N vs All
            if top_mode == "Top N":
                insight = insight.head(top_n)

            # Auto rotate x labels
            rot = smart_xtick_rotation(insight[group_by].tolist())

            # BAR: Total Spend
            st.markdown("#### Bar Chart — Total Spend")
            fig1 = px.bar(
                insight,
                x=group_by,
                y="total_spend_sum",
                hover_data=["transaksi_count", "total_spend_avg"],
                title=f"Total Spend by {group_by} ({top_mode})",
            )
            fig1.update_layout(xaxis_title=group_by, yaxis_title="Total Spend")
            fig1.update_xaxes(tickangle=rot)
            st.plotly_chart(fig1, use_container_width=True)

            # BAR: Jumlah Transaksi
            st.markdown("#### Bar Chart — Jumlah Transaksi")
            fig2 = px.bar(
                insight,
                x=group_by,
                y="transaksi_count",
                hover_data=["total_spend_sum", "total_spend_avg"],
                title=f"Jumlah Transaksi by {group_by} ({top_mode})",
            )
            fig2.update_layout(xaxis_title=group_by, yaxis_title="Jumlah Transaksi")
            fig2.update_xaxes(tickangle=rot)
            st.plotly_chart(fig2, use_container_width=True)

            # PIE: Total Spend / Transaksi
            st.markdown("#### Pie Chart — Proporsi")
            pie_value_col = "total_spend_sum" if pie_metric == "Total Spend" else "transaksi_count"
            fig3 = px.pie(
                insight,
                names=group_by,
                values=pie_value_col,
                hover_data=["total_spend_sum", "transaksi_count", "total_spend_avg"],
                title=f"Share {pie_metric} by {group_by} ({top_mode})",
            )
            st.plotly_chart(fig3, use_container_width=True)

            # Insight Table
            st.markdown("#### Tabel Insight")
            insight_disp = insight.copy()
            insight_disp["total_spend_sum"] = insight_disp["total_spend_sum"].astype(float).round(2)
            insight_disp["total_spend_avg"] = insight_disp["total_spend_avg"].astype(float).round(2)
            st.dataframe(insight_disp, use_container_width=True, height=360)

    show_preprocessing_notes()

else:
    go("home")
