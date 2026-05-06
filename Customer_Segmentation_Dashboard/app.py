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

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

h1, h2, h3 {
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #161A23;
}

.kpi-card {
    background: linear-gradient(135deg,#1f77b4,#6a11cb);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}

.small-text {
    font-size:14px;
    color:#dcdcdc;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🛍️ Customer Segmentation Dashboard")
st.markdown(
    "Analyze customer behavior using **K-Means Clustering** and advanced visual analytics."
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.title("⚙️ Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Dataset uploaded successfully!")

else:

    DATA_PATH = Path(__file__).parent / "Mall_Customers.csv"

    df = pd.read_csv(DATA_PATH)

    st.sidebar.info("Using default Mall Customers dataset.")

# ---------------------------------------------------
# DATA PREVIEW
# ---------------------------------------------------

st.subheader("📄 Dataset Preview")
st.dataframe(df.head())

# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

df = df.dropna()

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

col1, col2, col3 = st.columns(3)

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
        <h1>{round(df['Age'].mean(),1)}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <h3>Average Spending Score</h3>
        <h1>{round(df['Spending Score (1-100)'].mean(),1)}</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------
# FEATURE SELECTION
# ---------------------------------------------------

features = st.sidebar.multiselect(
    "Select Features for Clustering",
    options=[
        'Age',
        'Annual Income (k$)',
        'Spending Score (1-100)'
    ],
    default=[
        'Annual Income (k$)',
        'Spending Score (1-100)'
    ]
)

if len(features) < 2:
    st.warning("Please select at least 2 features.")
    st.stop()

X = df[features]

# ---------------------------------------------------
# STANDARDIZATION
# ---------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------------------------------------------------
# ELBOW METHOD
# ---------------------------------------------------

st.subheader("📉 Elbow Method")

wcss = []

for i in range(1, 11):

    kmeans = KMeans(
        n_clusters=i,
        init='k-means++',
        random_state=42,
        n_init=10
    )

    kmeans.fit(X_scaled)

    wcss.append(kmeans.inertia_)

fig_elbow = go.Figure()

fig_elbow.add_trace(go.Scatter(
    x=list(range(1,11)),
    y=wcss,
    mode='lines+markers'
))

fig_elbow.update_layout(
    template="plotly_dark",
    xaxis_title="Number of Clusters",
    yaxis_title="WCSS",
    height=500
)

st.plotly_chart(fig_elbow, use_container_width=True)

# ---------------------------------------------------
# K SELECTION
# ---------------------------------------------------

k = st.sidebar.slider(
    "Select Number of Clusters",
    min_value=2,
    max_value=10,
    value=5
)

# ---------------------------------------------------
# KMEANS MODEL
# ---------------------------------------------------

kmeans = KMeans(
    n_clusters=k,
    init='k-means++',
    random_state=42,
    n_init=10
)

y_kmeans = kmeans.fit_predict(X_scaled)

df['Cluster'] = y_kmeans

# ---------------------------------------------------
# SILHOUETTE SCORE
# ---------------------------------------------------

score = silhouette_score(X_scaled, y_kmeans)

st.subheader("📌 Clustering Evaluation")

col1, col2 = st.columns(2)

with col1:
    st.metric("Selected Clusters", k)

with col2:
    st.metric("Silhouette Score", round(score,3))

st.info("""
Silhouette Score measures how well customers fit within their clusters.
Values closer to 1 indicate better-defined clusters.
""")

# ---------------------------------------------------
# CUSTOMER SEGMENTS PLOT
# ---------------------------------------------------

st.subheader("🎯 Customer Segments")

fig = px.scatter(
    df,
    x=features[0],
    y=features[1],
    color=df['Cluster'].astype(str),
    template="plotly_dark",
    title="Customer Segmentation using K-Means",
    hover_data=df.columns
)

fig.update_layout(height=700)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# PCA VISUALIZATION
# ---------------------------------------------------

st.subheader("🧠 PCA Cluster Visualization")

pca = PCA(n_components=2)

pca_components = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame()

pca_df['PCA1'] = pca_components[:,0]
pca_df['PCA2'] = pca_components[:,1]
pca_df['Cluster'] = y_kmeans.astype(str)

fig_pca = px.scatter(
    pca_df,
    x='PCA1',
    y='PCA2',
    color='Cluster',
    template='plotly_dark',
    title='PCA Projection of Customer Clusters'
)

fig_pca.update_layout(height=700)

st.plotly_chart(fig_pca, use_container_width=True)

# ---------------------------------------------------
# CLUSTER SUMMARY
# ---------------------------------------------------

st.subheader("📊 Cluster Summary")

summary = df.groupby('Cluster')[features].mean()

st.dataframe(summary)

# ---------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------

st.subheader("💡 Business Insights")

for cluster in sorted(df['Cluster'].unique()):

    cluster_size = df[df['Cluster'] == cluster].shape[0]

    st.markdown(f"""
    ### Cluster {cluster}

    - Customers in this segment: **{cluster_size}**
    - Average profile based on selected features shown above.
    - Businesses can target this segment with personalized marketing strategies.

    ---
    """)

# ---------------------------------------------------
# DOWNLOAD DATA
# ---------------------------------------------------

st.subheader("⬇️ Download Segmented Dataset")

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download CSV",
    data=csv,
    file_name='segmented_customers.csv',
    mime='text/csv'
)
