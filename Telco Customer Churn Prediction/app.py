import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Churn Prediction Dashboard")
st.write(
    "Predict customer churn using supervised machine learning models "
    "and analyze model performance."
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

st.sidebar.header("📁 Dataset")

st.sidebar.markdown("""
### Dataset Requirements

Your CSV should contain:

- `Churn` column as target
- Customer details such as:
  - tenure
  - contract
  - charges
  - services

Optional:
- `customerID` column will be removed automatically.
""")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Uploaded dataset loaded!")
else:
    DATA_PATH = Path(__file__).parent / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
    df = pd.read_csv(DATA_PATH)
    st.sidebar.info("Using default churn dataset.")

# ---------------------------------------------------
# VALIDATION
# ---------------------------------------------------

if "Churn" not in df.columns:
    st.error("Dataset must contain a `Churn` column.")
    st.stop()

# ---------------------------------------------------
# PREVIEW
# ---------------------------------------------------

st.subheader("🔍 Dataset Preview")
st.dataframe(df.head())

# ---------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------

data = df.copy()

# Remove customerID
if "customerID" in data.columns:
    data = data.drop("customerID", axis=1)

# Convert TotalCharges
if "TotalCharges" in data.columns:
    data["TotalCharges"] = pd.to_numeric(
        data["TotalCharges"],
        errors="coerce"
    )

# Convert Churn safely
data["Churn"] = data["Churn"].replace({
    "No": 0,
    "Yes": 1
})

data["Churn"] = pd.to_numeric(
    data["Churn"],
    errors="coerce"
)

# Remove NaN
data = data.dropna(subset=["Churn"])

# Convert to int
data["Churn"] = data["Churn"].astype(int)

# Remove remaining NaN rows
data = data.dropna()

# ---------------------------------------------------
# LABEL ENCODING
# ---------------------------------------------------

label_encoders = {}

for col in data.columns:
    if data[col].dtype == "object":

        le = LabelEncoder()

        data[col] = le.fit_transform(data[col])

        label_encoders[col] = le

# ---------------------------------------------------
# DATASET INFO
# ---------------------------------------------------

st.subheader("🧹 Cleaned Dataset Info")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Rows", data.shape[0])

with col2:
    st.metric("Columns", data.shape[1])

with col3:
    churn_rate = data["Churn"].mean() * 100
    st.metric("Churn Rate", f"{churn_rate:.2f}%")

# ---------------------------------------------------
# FEATURES / TARGET
# ---------------------------------------------------

X = data.drop("Churn", axis=1)
y = data["Churn"]

# ---------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------

st.sidebar.header("⚙️ Controls")

test_size = st.sidebar.slider(
    "Test Size",
    0.10,
    0.40,
    0.20,
    0.05
)

threshold = st.sidebar.slider(
    "Decision Threshold",
    0.10,
    0.90,
    0.30,
    0.05
)

# ---------------------------------------------------
# TRAIN TEST SPLIT
# ---------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=test_size,
    random_state=42,
    stratify=y
)

# ---------------------------------------------------
# MODELS
# ---------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        class_weight="balanced",
        random_state=42
    )
}

results = []

trained_models = {}

# ---------------------------------------------------
# TRAIN MODELS
# ---------------------------------------------------

for name, model in models.items():

    model.fit(X_train, y_train)

    trained_models[name] = model

    probs = model.predict_proba(X_test)[:, 1]

    preds = (probs >= threshold).astype(int)

    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds),
        "Recall": recall_score(y_test, preds),
        "F1 Score": f1_score(y_test, preds),
        "AUC": roc_auc_score(y_test, probs)
    })

results_df = pd.DataFrame(results)

# ---------------------------------------------------
# MODEL COMPARISON
# ---------------------------------------------------

st.subheader("📊 Model Comparison")

st.dataframe(results_df)

fig_compare, ax_compare = plt.subplots(figsize=(8, 4))

ax_compare.bar(
    results_df["Model"],
    results_df["Recall"]
)

ax_compare.set_title("Recall Comparison")
ax_compare.set_ylabel("Recall")
ax_compare.set_ylim(0, 1)

for i, v in enumerate(results_df["Recall"]):
    ax_compare.text(i, v + 0.02, f"{v:.2f}", ha="center")

st.pyplot(fig_compare)

# ---------------------------------------------------
# MODEL SELECTION
# ---------------------------------------------------

selected_model_name = st.sidebar.selectbox(
    "Select Model",
    list(models.keys()),
    index=1
)

selected_model = trained_models[selected_model_name]

y_probs = selected_model.predict_proba(X_test)[:, 1]

y_pred = (y_probs >= threshold).astype(int)

# ---------------------------------------------------
# METRICS
# ---------------------------------------------------

st.subheader(f"📌 Detailed Evaluation: {selected_model_name}")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Accuracy",
        f"{accuracy_score(y_test, y_pred):.2f}"
    )

with c2:
    st.metric(
        "Precision",
        f"{precision_score(y_test, y_pred):.2f}"
    )

with c3:
    st.metric(
        "Recall",
        f"{recall_score(y_test, y_pred):.2f}"
    )

with c4:
    st.metric(
        "F1 Score",
        f"{f1_score(y_test, y_pred):.2f}"
    )

with c5:
    st.metric(
        "AUC",
        f"{roc_auc_score(y_test, y_probs):.2f}"
    )

# ---------------------------------------------------
# CONFUSION MATRIX
# ---------------------------------------------------

st.subheader("🧩 Confusion Matrix")

cm = confusion_matrix(y_test, y_pred)

fig_cm, ax_cm = plt.subplots(figsize=(5, 4))

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Stay", "Churn"]
)

disp.plot(ax=ax_cm)

st.pyplot(fig_cm)

# ---------------------------------------------------
# ROC CURVE
# ---------------------------------------------------

st.subheader("📈 ROC Curve")

fpr, tpr, _ = roc_curve(y_test, y_probs)

auc = roc_auc_score(y_test, y_probs)

fig_roc, ax_roc = plt.subplots(figsize=(6, 4))

ax_roc.plot(fpr, tpr, label=f"AUC = {auc:.2f}")

ax_roc.plot([0, 1], [0, 1], linestyle="--")

ax_roc.set_xlabel("False Positive Rate")
ax_roc.set_ylabel("True Positive Rate")
ax_roc.set_title("ROC Curve")

ax_roc.legend()

st.pyplot(fig_roc)

# ---------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------

if selected_model_name == "Random Forest":

    st.subheader("🔥 Feature Importance")

    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": selected_model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="Importance",
        ascending=False
    )

    st.dataframe(importance_df)

    fig_imp, ax_imp = plt.subplots(figsize=(8, 5))

    top_features = importance_df.head(10)

    ax_imp.barh(
        top_features["Feature"],
        top_features["Importance"]
    )

    ax_imp.invert_yaxis()

    ax_imp.set_title("Top 10 Important Features")

    st.pyplot(fig_imp)

# ---------------------------------------------------
# PREDICTION UI
# ---------------------------------------------------

st.subheader("🔮 Predict Churn for a Customer")

st.write(
    "Enter customer details below to predict churn probability."
)

col1, col2, col3 = st.columns(3)

with col1:

    gender = st.selectbox(
        "Gender",
        ["Female", "Male"]
    )

    senior_citizen = st.selectbox(
        "Senior Citizen",
        ["No", "Yes"]
    )

    partner = st.selectbox(
        "Partner",
        ["No", "Yes"]
    )

    dependents = st.selectbox(
        "Dependents",
        ["No", "Yes"]
    )

    tenure = st.slider(
        "Tenure (Months)",
        0,
        72,
        12
    )

with col2:

    phone_service = st.selectbox(
        "Phone Service",
        ["No", "Yes"]
    )

    multiple_lines = st.selectbox(
        "Multiple Lines",
        ["No", "Yes", "No phone service"]
    )

    internet_service = st.selectbox(
        "Internet Service",
        ["DSL", "Fiber optic", "No"]
    )

    online_security = st.selectbox(
        "Online Security",
        ["No", "Yes", "No internet service"]
    )

    online_backup = st.selectbox(
        "Online Backup",
        ["No", "Yes", "No internet service"]
    )

with col3:

    device_protection = st.selectbox(
        "Device Protection",
        ["No", "Yes", "No internet service"]
    )

    tech_support = st.selectbox(
        "Tech Support",
        ["No", "Yes", "No internet service"]
    )

    streaming_tv = st.selectbox(
        "Streaming TV",
        ["No", "Yes", "No internet service"]
    )

    streaming_movies = st.selectbox(
        "Streaming Movies",
        ["No", "Yes", "No internet service"]
    )

    contract = st.selectbox(
        "Contract",
        ["Month-to-month", "One year", "Two year"]
    )

col4, col5, col6 = st.columns(3)

with col4:

    paperless_billing = st.selectbox(
        "Paperless Billing",
        ["No", "Yes"]
    )

with col5:

    payment_method = st.selectbox(
        "Payment Method",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)"
        ]
    )

with col6:

    monthly_charges = st.number_input(
        "Monthly Charges",
        min_value=0.0,
        value=70.0
    )

    total_charges = st.number_input(
        "Total Charges",
        min_value=0.0,
        value=1000.0
    )

# ---------------------------------------------------
# INPUT DATAFRAME
# ---------------------------------------------------

input_raw = pd.DataFrame({

    "gender": [gender],

    "SeniorCitizen": [
        1 if senior_citizen == "Yes" else 0
    ],

    "Partner": [partner],

    "Dependents": [dependents],

    "tenure": [tenure],

    "PhoneService": [phone_service],

    "MultipleLines": [multiple_lines],

    "InternetService": [internet_service],

    "OnlineSecurity": [online_security],

    "OnlineBackup": [online_backup],

    "DeviceProtection": [device_protection],

    "TechSupport": [tech_support],

    "StreamingTV": [streaming_tv],

    "StreamingMovies": [streaming_movies],

    "Contract": [contract],

    "PaperlessBilling": [paperless_billing],

    "PaymentMethod": [payment_method],

    "MonthlyCharges": [monthly_charges],

    "TotalCharges": [total_charges]
})

input_encoded = input_raw.copy()

for col in input_encoded.columns:

    if col in label_encoders:

        input_encoded[col] = label_encoders[col].transform(
            input_encoded[col]
        )

input_encoded = input_encoded[X.columns]

# ---------------------------------------------------
# PREDICTION
# ---------------------------------------------------

if st.button("Predict Churn"):

    churn_prob = selected_model.predict_proba(
        input_encoded
    )[0][1]

    prediction = 1 if churn_prob >= threshold else 0

    st.metric(
        "Churn Probability",
        f"{churn_prob * 100:.2f}%"
    )

    if prediction == 1:

        st.error(
            "Customer is likely to churn ❌"
        )

    else:

        st.success(
            "Customer is likely to stay ✅"
        )

# ---------------------------------------------------
# BUSINESS INSIGHT
# ---------------------------------------------------

st.subheader("🧠 Business Insight")

st.write("""
This dashboard compares supervised learning models
for customer churn prediction.

Since churn prediction is a business risk problem,
recall is emphasized to identify more customers
who are likely to leave.

Random Forest provides strong performance and
feature importance, helping identify key churn
drivers such as tenure, charges, and contract
features.
""")
