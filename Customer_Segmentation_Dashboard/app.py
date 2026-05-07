import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="🛍️",
    layout="wide"
)

st.markdown("""
<style>

/* MAIN */
.main {
    background-color: #0E1117;
    color: white;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0f172a,#020617);
    padding: 28px;
    width: 340px !important;
}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* SIDEBAR TITLE */
.sidebar-title {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 35px;
    line-height: 1.4;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background-color: #172033;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 22px;
}

/* UPLOAD BUTTON */
[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg,#2563eb,#7c3aed);
    color: white !important;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}

/* INFO BOX */
.stAlert {
    border-radius: 15px;
    margin-top: 15px;
}

/* MULTISELECT */
.stMultiSelect div[data-baseweb="select"] {
    background-color: #172033 !important;
    border: 1px solid #334155 !important;
    border-radius: 15px !important;
    min-height: 60px;
}

/* SLIDER */
.stSlider {
    padding-top: 20px;
    padding-bottom: 25px;
}

/* KPI CARDS */
.kpi-card {
    background: linear-gradient(135deg,#2563eb,#7c3aed);
    padding: 25px;
    border-radius: 20px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.4);
}

/* METRICS */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 18px;
}

/* BUTTONS */
.stButton button {
    background: linear-gradient(135deg,#2563eb,#7c3aed);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 10px 22px;
}

.stDownloadButton button {
    background: linear-gradient(135deg,#059669,#10b981);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 10px 22px;
}

/* HEADINGS */
h1 {
    color: white;
    font-weight: 800;
}

h2, h3 {
    color: #E2E8F0;
}

/* REMOVE TOP GAP */
.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

st.title("🛍️ Customer Segmentation Dashboard")
st.markdown(
    "Analyze customer behavior using **K-Means Clustering** and advanced visual analytics."
)

st.sidebar.markdown(
    '<div class="sidebar-title">⚙ Dashboard Controls</div>',
    unsafe_allow_html=True
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Dataset uploaded successfully!")
else:
    DATA_PATH = Path(__file__).parent / "Mall_Customers.csv"
    df = pd.read_csv(DATA_PATH)
    st.sidebar.info("Using default Mall Customers dataset.")

st.subheader("📄 Dataset Preview")
st.dataframe(df.head())

required_columns = [
    "Gender",
    "Age",
    "Annual Income (k$)",
    "Spending Score (1-100)"
]

if not all(col in df.columns for col in required_columns):
    st.error("Dataset must contain Gender, Age, Annual Income (k$), and Spending Score (1-100).")
    st.stop()

df["Gender"] = df["Gender"].fillna(df["Gender"].mode()[0])
df["Age"] = df["Age"].fillna(df["Age"].mean())
df["Annual Income (k$)"] = df["Annual Income (k$)"].fillna(
    df["Annual Income (k$)"].mean()
)
df["Spending Score (1-100)"] = df["Spending Score (1-100)"].fillna(
    df["Spending Score (1-100)"].mean()
)

st.subheader("📊 Dashboard Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Total Customers</h3>
        <h1>{df.shape[0]}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Average Age</h3>
        <h1>{df['Age'].mean():.1f}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Average Income</h3>
        <h1>{df['Annual Income (k$)'].mean():.1f}k</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Spending Score</h3>
        <h1>{df['Spending Score (1-100)'].mean():.1f}</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

features = st.sidebar.multiselect(
    "Select Features for Clustering",
    options=[
        "Age",
        "Annual Income (k$)",
        "Spending Score (1-100)"
    ],
    default=[
        "Annual Income (k$)",
        "Spending Score (1-100)"
    ]
)

if len(features) < 2:
    st.warning("Please select at least 2 features.")
    st.stop()

X = df[features]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

st.subheader("📉 Elbow Method")

wcss = []

for i in range(1, 11):
    kmeans_temp = KMeans(
        n_clusters=i,
        init="k-means++",
        random_state=42,
        n_init=10
    )
    kmeans_temp.fit(X_scaled)
    wcss.append(kmeans_temp.inertia_)

fig_elbow = go.Figure()

fig_elbow.add_trace(go.Scatter(
    x=list(range(1, 11)),
    y=wcss,
    mode="lines+markers"
))

fig_elbow.update_layout(
    template="plotly_dark",
    xaxis_title="Number of Clusters",
    yaxis_title="WCSS",
    height=500
)

st.plotly_chart(fig_elbow, use_container_width=True)

k = st.sidebar.slider(
    "Select Number of Clusters",
    min_value=2,
    max_value=10,
    value=5
)

kmeans = KMeans(
    n_clusters=k,
    init="k-means++",
    random_state=42,
    n_init=10
)

y_kmeans = kmeans.fit_predict(X_scaled)
df["Cluster"] = y_kmeans

score = silhouette_score(X_scaled, y_kmeans)

st.subheader("📌 Clustering Evaluation")

eval_col1, eval_col2 = st.columns(2)

with eval_col1:
    st.metric("Selected Clusters", k)

with eval_col2:
    st.metric("Silhouette Score", f"{score:.3f}")

st.info(
    "Silhouette Score measures how well customers fit within their clusters. "
    "Values closer to 1 indicate better-defined clusters."
)

st.subheader("🎯 Customer Segments")

fig = px.scatter(
    df,
    x=features[0],
    y=features[1],
    color=df["Cluster"].astype(str),
    template="plotly_dark",
    title="Customer Segmentation using K-Means",
    hover_data=df.columns
)

fig.update_layout(height=700)

st.plotly_chart(fig, use_container_width=True)

st.subheader("🧠 PCA Cluster Visualization")

pca = PCA(n_components=2)
pca_components = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame({
    "PCA1": pca_components[:, 0],
    "PCA2": pca_components[:, 1],
    "Cluster": y_kmeans.astype(str)
})

fig_pca = px.scatter(
    pca_df,
    x="PCA1",
    y="PCA2",
    color="Cluster",
    template="plotly_dark",
    title="PCA Projection of Customer Clusters"
)

fig_pca.update_layout(height=700)

st.plotly_chart(fig_pca, use_container_width=True)

st.subheader("📊 Cluster Distribution")

cluster_counts = df["Cluster"].value_counts().sort_index()

fig_bar = px.bar(
    x=cluster_counts.index.astype(str),
    y=cluster_counts.values,
    color=cluster_counts.index.astype(str),
    template="plotly_dark",
    labels={
        "x": "Cluster",
        "y": "Number of Customers"
    },
    title="Number of Customers in Each Cluster"
)

st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📋 Cluster Summary")

summary = df.groupby("Cluster")[features].mean()
st.dataframe(summary)

st.subheader("💡 Business Insights")

for cluster in sorted(df["Cluster"].unique()):
    cluster_size = df[df["Cluster"] == cluster].shape[0]

    st.markdown(f"""
    ### Cluster {cluster}

    - Customers in this segment: **{cluster_size}**
    - Average profile is shown in the cluster summary table.
    - Businesses can target this group with personalized marketing strategies.

    ---
    """)

st.subheader("⬇️ Download Segmented Dataset")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="segmented_customers.csv",
    mime="text/csv"
)

st.markdown("---")

st.subheader("⭐ Project Summary")

st.write("""
This dashboard uses K-Means clustering to identify hidden customer groups based on purchasing behavior.

Features included:
- Interactive clustering dashboard
- Elbow Method visualization
- Silhouette Score evaluation
- PCA visualization
- Business insight generation
- Downloadable segmented dataset
""")
