# Advanced Streamlit UI Upgrades for Customer Segmentation Dashboard


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown(
    """
    <style>

    .main {
        background-color: #0E1117;
        color: white;
    }

    h1, h2, h3 {
        color: white;
    }

    .metric-card {
        background: linear-gradient(135deg, #1f77ff, #7f5af0);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    .insight-card {
        background-color: #1c1f26;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #7f5af0;
        margin-bottom: 10px;
        color: white;
    }

    .stDataFrame {
        background-color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("🛍️ Customer Segmentation Dashboard")
st.write(
    "Analyze customer behavior using K-Means clustering and advanced visual analytics."
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
    df = pd.read_csv("Mall_Customers.csv")
    st.sidebar.info("Using default Mall Customers dataset")

# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

required_columns = [
    "Gender",
    "Age",
    "Annual Income (k$)",
    "Spending Score (1-100)"
]

if not all(col in df.columns for col in required_columns):
    st.error(
        "Dataset must contain Gender, Age, Annual Income (k$), and Spending Score (1-100)."
    )
    st.stop()

# Fill missing values

df["Gender"] = df["Gender"].fillna(df["Gender"].mode()[0])

df["Age"] = df["Age"].fillna(df["Age"].mean())

df["Annual Income (k$)"] = df["Annual Income (k$)"].fillna(
    df["Annual Income (k$)"].mean()
)

df["Spending Score (1-100)"] = df[
    "Spending Score (1-100)"
].fillna(df["Spending Score (1-100)"].mean())

# ---------------------------------------------------
# DATASET PREVIEW
# ---------------------------------------------------

st.subheader("📄 Dataset Preview")
st.dataframe(df.head())

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------

st.subheader("📊 Dashboard Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Total Customers</h3>
            <h1>{df.shape[0]}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Average Age</h3>
            <h1>{df['Age'].mean():.1f}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Average Income</h3>
            <h1>{df['Annual Income (k$)'].mean():.1f}k</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>Spending Score</h3>
            <h1>{df['Spending Score (1-100)'].mean():.1f}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# CLUSTER SETTINGS
# ---------------------------------------------------

st.sidebar.subheader("🎯 Clustering Settings")

k_value = st.sidebar.slider(
    "Select Number of Clusters",
    min_value=2,
    max_value=10,
    value=5
)

selected_features = st.sidebar.multiselect(
    "Select Features",
    [
        "Age",
        "Annual Income (k$)",
        "Spending Score (1-100)"
    ],
    default=[
        "Annual Income (k$)",
        "Spending Score (1-100)"
    ]
)

if len(selected_features) < 2:
    st.warning("Please select at least 2 features")
    st.stop()

X = df[selected_features]

# ---------------------------------------------------
# ELBOW METHOD
# ---------------------------------------------------

st.subheader("📉 Elbow Method")

wcss = []

for i in range(1, 11):

    kmeans_temp = KMeans(
        n_clusters=i,
        random_state=42,
        n_init=10
    )

    kmeans_temp.fit(X)

    wcss.append(kmeans_temp.inertia_)

fig_elbow = px.line(
    x=list(range(1, 11)),
    y=wcss,
    markers=True,
    title="Elbow Method"
)

fig_elbow.update_layout(
    template="plotly_dark",
    xaxis_title="Number of Clusters",
    yaxis_title="WCSS"
)

st.plotly_chart(fig_elbow, use_container_width=True)

# ---------------------------------------------------
# KMEANS MODEL
# ---------------------------------------------------

kmeans = KMeans(
    n_clusters=k_value,
    random_state=42,
    n_init=10
)

clusters = kmeans.fit_predict(X)

df["Cluster"] = clusters

# ---------------------------------------------------
# SILHOUETTE SCORE
# ---------------------------------------------------

st.subheader("📌 Clustering Evaluation")

sil_score = silhouette_score(X, clusters)

c1, c2 = st.columns(2)

with c1:
    st.metric("Selected Clusters", k_value)

with c2:
    st.metric("Silhouette Score", round(sil_score, 3))

# ---------------------------------------------------
# CUSTOMER SEGMENTS PLOT
# ---------------------------------------------------

st.subheader("🎯 Customer Segments")

if len(selected_features) == 2:

    fig_cluster = px.scatter(
        df,
        x=selected_features[0],
        y=selected_features[1],
        color=df["Cluster"].astype(str),
        title="Customer Segmentation",
        template="plotly_dark",
        size_max=12
    )

    centers = kmeans.cluster_centers_

    fig_cluster.add_trace(
        go.Scatter(
            x=centers[:, 0],
            y=centers[:, 1],
            mode='markers',
            marker=dict(
                color='red',
                size=18,
                symbol='x'
            ),
            name='Centroids'
        )
    )

    st.plotly_chart(fig_cluster, use_container_width=True)

else:

    pca = PCA(n_components=2)

    X_pca = pca.fit_transform(X)

    pca_df = pd.DataFrame(
        X_pca,
        columns=['PCA1', 'PCA2']
    )

    pca_df['Cluster'] = clusters.astype(str)

    fig_pca = px.scatter(
        pca_df,
        x='PCA1',
        y='PCA2',
        color='Cluster',
        title='PCA Visualization',
        template='plotly_dark'
    )

    st.plotly_chart(fig_pca, use_container_width=True)

# ---------------------------------------------------
# CLUSTER DISTRIBUTION
# ---------------------------------------------------

st.subheader("📊 Cluster Distribution")

cluster_counts = df['Cluster'].value_counts().sort_index()

fig_bar = px.bar(
    x=cluster_counts.index.astype(str),
    y=cluster_counts.values,
    color=cluster_counts.index.astype(str),
    template='plotly_dark',
    labels={
        'x': 'Cluster',
        'y': 'Customers'
    }
)

st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------
# CLUSTER SUMMARY
# ---------------------------------------------------

st.subheader("📋 Cluster Summary")

cluster_summary = df.groupby('Cluster')[
    ['Age', 'Annual Income (k$)', 'Spending Score (1-100)']
].mean()

st.dataframe(cluster_summary)

# ---------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------

st.subheader("🧠 Business Recommendations")

for cluster_id, row in cluster_summary.iterrows():

    income = row['Annual Income (k$)']
    spending = row['Spending Score (1-100)']

    if income >= 80 and spending >= 50:

        message = (
            f"Cluster {cluster_id}: Premium high-income and high-spending customers. "
            "Target them with VIP rewards and luxury promotions."
        )

    elif income >= 80 and spending < 40:

        message = (
            f"Cluster {cluster_id}: High-income but low-spending customers. "
            "Use personalized recommendations and engagement campaigns."
        )

    elif income < 40 and spending >= 50:

        message = (
            f"Cluster {cluster_id}: Young impulsive buyers with lower income but high spending. "
            "Respond well to discounts and social media campaigns."
        )

    else:

        message = (
            f"Cluster {cluster_id}: Moderate customer segment with balanced spending behavior."
        )

    st.markdown(
        f"""
        <div class="insight-card">
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# DOWNLOAD BUTTON
# ---------------------------------------------------

st.subheader("📥 Download Segmented Dataset")

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label='Download CSV',
    data=csv,
    file_name='segmented_customers.csv',
    mime='text/csv'
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown("---")

st.markdown(
    """
    ### ⭐ Project Summary

    This dashboard uses K-Means clustering to identify hidden customer groups based on purchasing behavior.

    Features included:
    - Interactive clustering dashboard
    - Elbow Method visualization
    - Silhouette Score evaluation
    - PCA visualization
    - Business recommendation engine
    - Downloadable segmented dataset
    - Professional Plotly visualizations
    """
)

