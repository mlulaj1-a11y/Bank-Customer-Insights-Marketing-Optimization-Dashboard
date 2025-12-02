import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Bank Customer Insights & Marketing Optimization Dashboard",
    page_icon=None,
    layout="wide"
)

# ---------------------------------------------------
# Title & Authors
# ---------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; font-weight:bold;'>Bank Customer Insights & Marketing Optimization Dashboard</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align:center; color:gray;'>Created by: Leah Alaimo • Michael Lulaj • Eleni Proios</h4>",
    unsafe_allow_html=True
)

# ---------------------------------------------------
# Load Data
# ---------------------------------------------------
df = pd.read_csv("bank-additional-full copy.csv", sep=';', encoding='latin1')
df.columns = df.columns.str.strip()

# ---------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------
st.sidebar.header("Filter Options")

# Age slider
min_age = int(df['age'].min())
max_age = int(df['age'].max())
age_range = st.sidebar.slider("Select Age Range:", min_age, max_age, (min_age, max_age))

# Job filter
job_options = sorted(df['job'].unique().tolist())
selected_jobs = st.sidebar.multiselect("Select Job Types:", job_options, default=job_options)

# Month filter (if available)
if "month" in df.columns:
    month_options = sorted(df["month"].unique().tolist())
    selected_months = st.sidebar.multiselect(
        "Campaign Months:", month_options, default=month_options
    )
else:
    selected_months = None

# ---------------------------------------------------
# Apply Filters
# ---------------------------------------------------
filtered = df[
    (df['age'] >= age_range[0]) &
    (df['age'] <= age_range[1]) &
    (df['job'].isin(selected_jobs))
]

if selected_months is not None:
    filtered = filtered[filtered["month"].isin(selected_months)]

# ---------------------------------------------------
# Metric Summary
# ---------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", len(df))
col2.metric("Filtered Customers", len(filtered))
col3.metric("Job Types Selected", len(selected_jobs))

# ---------------------------------------------------
# Insight Highlights
# ---------------------------------------------------
avg_age = filtered["age"].mean()
top_job = filtered["job"].mode()[0] if not filtered.empty else "N/A"
subscription_rate = (
    filtered["y"].value_counts(normalize=True).get("yes", 0) * 100
    if "y" in filtered.columns else None
)

st.info(f"""
**Insight Highlights**

- Average age of selected customers: {avg_age:.1f}  
- Most common job in this customer segment: {top_job}  
- Estimated subscription likelihood (term deposit): {subscription_rate:.2f}%  
""")

# ---------------------------------------------------
# Tabs for Navigation
# ---------------------------------------------------
tab_overview, tab_data, tab_visuals, tab_corr = st.tabs(
    ["Overview", "Data Sample", "Visualizations", "Correlations"]
)

# ---------------------------------------------------
# Overview Tab
# ---------------------------------------------------
with tab_overview:
    st.subheader("Summary of Current Filters")
    st.write(f"- Age range: {age_range[0]}–{age_range[1]}")
    st.write(f"- Selected jobs: {', '.join(selected_jobs)}")
    if selected_months is not None:
        st.write(f"- Selected months: {', '.join(selected_months)}")
    
    st.write("---")
    st.write("Job Distribution (Filtered Data)")
    fig_overview = px.pie(
        filtered,
        names="job",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_overview, use_container_width=True)

# ---------------------------------------------------
# Data Sample Tab
# ---------------------------------------------------
with tab_data:
    st.subheader("Filtered Data Preview")
    st.dataframe(filtered.head(15), use_container_width=True)

    with st.expander("Interpretation"):
        st.write("""
        This table shows the first 15 customers that match your selected filters.  
        Use it to explore individual-level data before diving into visual analytics.
        """)

# ---------------------------------------------------
# Visualizations Tab
# ---------------------------------------------------
with tab_visuals:
    st.subheader("Age Distribution by Job Type")
    fig1 = px.histogram(
        filtered,
        x="age",
        color="job",
        nbins=20,
        barmode="overlay",
        opacity=0.75
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Job Counts")
    job_counts = filtered["job"].value_counts().reset_index()
    job_counts.columns = ["job", "count"]

    sort_type = st.radio("Sort Jobs By:", ["Alphabetical", "Most Common"], horizontal=True)
    if sort_type == "Most Common":
        job_counts = job_counts.sort_values("count", ascending=False)

    fig2 = px.bar(
        job_counts,
        x="job",
        y="count",
        color="count",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# Correlation Tab
# ---------------------------------------------------
with tab_corr:
    st.subheader("Correlation Heatmap")

    numeric_cols = filtered.select_dtypes(include='number')

    if numeric_cols.empty:
        st.warning("Not enough numeric data available for a correlation heatmap.")
    else:
        corr_matrix = numeric_cols.corr()
        fig3 = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=px.colors.sequential.Cividis
        )
        st.plotly_chart(fig3, use_container_width=True)

    with st.expander("How to Read This"):
        st.write("""
        - Values close to 1.0 indicate strong positive relationships  
        - Values close to -1.0 indicate strong negative relationships  
        - This matrix helps identify which variables influence each other  
        """)

