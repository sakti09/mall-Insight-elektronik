import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Cluster", layout="wide")

# load css khusus halaman cluster
def load_css(css_path: str):
    p = Path(css_path)
    if p.exists():
        st.markdown(f"<style>{p.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

load_css("assets/insight.css")

st.title("Cluster Dashboard")
st.caption("Visualisasi hasil clustering Fuzzy C-Means dan interpretasi cluster.")

# fungsi bantu
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

# upload data cluster
st.sidebar.header("Upload Data")
uploaded = st.sidebar.file_uploader("Upload CSV hasil clustering (FCM)", type=["csv"])

if uploaded is None:
    st.info("Silakan upload file CSV hasil clustering.")
    st.stop()

df = pd.read_csv(uploaded)
st.sidebar.success("CSV berhasil diupload")

# deteksi kolom penting
cluster_col = pick_col(df, ["cluster", "cluster_label", "class"])
spend_col   = pick_col(df, ["total_spent", "total_spend", "spend", "amount"])

if cluster_col is None:
    st.error("Kolom cluster tidak ditemukan.")
    st.stop()

df[cluster_col] = df[cluster_col].astype(str)

# filter data
st.sidebar.header("Filters")
clusters = sorted(df[cluster_col].unique().tolist())
selected_clusters = st.sidebar.multiselect("Cluster", clusters, clusters)

df_f = df.copy()
df_f = df_f[df_f[cluster_col].isin(selected_clusters)]

st.sidebar.caption(f"Filtered rows: {len(df_f):,} / {len(df):,}")

# preview data
with st.expander("Preview data (head)", expanded=False):
    st.dataframe(df_f.head(25), use_container_width=True)

# ringkasan KPI
st.subheader("Ringkasan")

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi("Jumlah Data", fmt_int(len(df_f)))
with k2:
    render_kpi("Jumlah Cluster", fmt_int(len(selected_clusters)))
with k3:
    render_kpi("Total Spend", fmt_money(ensure_numeric(df_f[spend_col]).sum()) if spend_col else "-")
with k4:
    render_kpi("Rata-rata Spend", fmt_money(ensure_numeric(df_f[spend_col]).mean()) if spend_col else "-")

# visual overview cluster
st.subheader("Cluster Overview")

left, right = st.columns(2)

with left:
    vc = safe_value_counts(df_f[cluster_col]).reset_index()
    vc.columns = [cluster_col, "count"]
    fig = px.bar(vc, x=cluster_col, y="count", title="Jumlah Data per Cluster")
    st.plotly_chart(fig, use_container_width=True)

with right:
    if spend_col:
        grp = df_f.groupby(cluster_col)[spend_col].sum().reset_index()
        fig = px.bar(grp, x=cluster_col, y=spend_col, title="Total Spend per Cluster")
        st.plotly_chart(fig, use_container_width=True)

# interpretasi cluster
st.subheader("Interpretasi Cluster")

st.markdown(
    """
    <div class="quote-box">
        “Cluster terbentuk dari kombinasi usia dan perilaku belanja, sehingga masing-masing cluster merepresentasikan
        tipe pelanggan yang berbeda, mulai dari pelanggan impulsif bernilai rendah hingga pelanggan premium bernilai tinggi.”
    </div>
    """,
    unsafe_allow_html=True
)

# tabel ringkas + keterangan cluster
cluster_table = pd.DataFrame(
    [
        {
            "Cluster": "0",
            "Judul": "Senior Practical Shoppers",
            "Inti": "Tua, belanja sedikit, stabil",
            "Keterangan": "Pelanggan berusia lebih tua dengan pembelian rendah dan selektif. Segmen ini cenderung stabil namun kontribusi terhadap nilai transaksi relatif kecil."
        },
        {
            "Cluster": "1",
            "Judul": "Active Young Buyers",
            "Inti": "Muda, aktif, potensial",
            "Keterangan": "Pelanggan muda yang aktif berbelanja dengan nilai menengah. Memiliki potensi besar untuk dikembangkan menjadi pelanggan loyal melalui program retensi."
        },
        {
            "Cluster": "2",
            "Judul": "Stable Mature Customers",
            "Inti": "Dewasa, konsisten",
            "Keterangan": "Pelanggan dewasa dengan pola belanja yang konsisten dan terencana. Cocok untuk strategi membership dan personalisasi penawaran."
        },
        {
            "Cluster": "3",
            "Judul": "Impulse Young Shoppers",
            "Inti": "Muda, impulsif",
            "Keterangan": "Pelanggan muda dengan nilai belanja rendah dan pembelian cepat. Umumnya membeli karena kebutuhan kecil atau dorongan impulsif."
        },
        {
            "Cluster": "4",
            "Judul": "Premium High-Value Customers",
            "Inti": "Sedikit tapi sangat bernilai",
            "Keterangan": "Pelanggan bernilai tertinggi dengan total belanja sangat besar. Walaupun jumlahnya sedikit, kontribusinya terhadap pendapatan sangat signifikan."
        },
    ]
)

st.markdown("<div class='panel-title'>Ringkasan Profil Cluster</div>", unsafe_allow_html=True)

rows_html = ""
for _, r in cluster_table.iterrows():
    rows_html += f"""
    <tr>
        <td class="td-cluster">{r['Cluster']}</td>
        <td class="td-judul">{r['Judul']}</td>
        <td class="td-inti">{r['Inti']}</td>
        <td class="td-keterangan">{r['Keterangan']}</td>
    </tr>
    """

st.markdown(
    f"""
    <div class="table-wrap">
        <table class="cluster-table">
            <thead>
                <tr>
                    <th class="th-cluster">Cluster</th>
                    <th>Judul</th>
                    <th>Inti</th>
                    <th>Keterangan</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("Data sumber: CSV hasil clustering Fuzzy C-Means")
