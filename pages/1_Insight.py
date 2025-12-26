import streamlit as st
import pandas as pd
from src.insight_awal import build_insights

st.title("Page 1 - Insight")

uploaded = st.file_uploader("Upload file CSV", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    st.subheader("Preview Data")
    st.dataframe(df.head(20), use_container_width=True)

    insights = build_insights(df)

    st.subheader("Ringkasan")
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", insights["n_rows"])
    c2.metric("Columns", insights["n_cols"])
    c3.metric("Missing Cells", insights["missing_cells"])

    if insights["corr"] is not None:
        st.subheader("Correlation Matrix")
        st.dataframe(insights["corr"], use_container_width=True)
else:
    st.info("Upload CSV dulu untuk melihat insight.")
