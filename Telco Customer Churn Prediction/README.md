# 📊 Customer Churn Prediction Dashboard

An end-to-end supervised machine learning project for predicting customer churn using classification models and an interactive Streamlit dashboard.

---

## 🚀 Live Demo
🔗 Streamlit App: [[Add Your Streamlit Link Here]](http://localhost:8501/)

---

## 📌 Project Overview

Customer churn prediction is an important business problem in telecom and subscription-based industries. This project predicts whether a customer is likely to churn based on customer demographics, contract details, services, and billing information.

The application allows users to:

- Upload their own churn dataset
- Compare machine learning models
- Analyze model performance
- Predict churn probability for new customers
- Visualize business insights interactively

---

## ✨ Features

✅ Upload custom CSV datasets  
✅ Automatic preprocessing and encoding  
✅ Multiple supervised ML models  
✅ Model comparison dashboard  
✅ Interactive churn prediction UI  
✅ Confusion Matrix visualization  
✅ ROC Curve analysis  
✅ Feature importance visualization  
✅ Adjustable classification threshold  
✅ Business insight interpretation  

---

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Streamlit

---

## 📂 Dataset

Dataset Used:
**Telco Customer Churn Dataset**

The dataset contains:

- Customer demographics
- Contract information
- Internet services
- Billing details
- Customer tenure
- Churn status

---

## 🤖 Machine Learning Models

### 1️⃣ Logistic Regression
- Baseline linear classification model

### 2️⃣ Random Forest Classifier
- Ensemble tree-based model
- Selected as the best-performing model

---

## 📈 Model Evaluation

The models were evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC Score
- Confusion Matrix
- ROC Curve

### 📊 Final Random Forest Performance

| Metric | Score |
|---|---|
| Accuracy | ~74% |
| ROC-AUC | 0.81 |
| Recall | Improved using threshold tuning |

---

## 🔥 Key Insights

The model identified major churn-driving factors such as:

- Tenure
- Monthly Charges
- Total Charges
- Contract Type

Customers with short tenure and month-to-month contracts showed higher churn probability.

---

## 💼 Business Value

This project helps businesses:

- Identify high-risk customers
- Improve retention strategies
- Reduce customer loss
- Support proactive customer engagement

---

## 🖥️ Streamlit Dashboard

The dashboard includes:

- Interactive model comparison
- Customer churn prediction system
- ROC and confusion matrix visualization
- Feature importance analysis
- Real-time churn probability prediction

---

## ▶️ How to Run the Project

### 1️⃣ Clone Repository

```bash
git clone https://github.com/15Aakash/Project.git
