# Spotify Song Popularity Prediction and Clustering

This project was developed as part of the INFO 648 Business Data Analytics course at Virginia Commonwealth University. The objective was to assist Spotify in improving its recommendation engine by predicting the popularity of newly released songs and uncovering key feature patterns.

## Project Objectives
1. Predict whether a song’s popularity score is 65 or above using machine learning models.
2. Choose the best model based on both accuracy and financial impact.
3. Use clustering to study how musical features influence popularity.
4. Identify feature patterns associated with high or low popularity songs.

## Dataset
- Source: `songs_utf.csv` – Spotify U.S. top chart songs from 1998–2020.
- Features: Acousticness, danceability, energy, loudness, tempo, genre flags, and more.

## Key Contributions
- Built classification models: Logistic Regression, Decision Tree, and K-Nearest Neighbors.
- Evaluated models based on accuracy and business-defined profit/loss.
- Applied K-Means clustering on danceability and energy to study the impact of valence.
- Performed association analysis to identify traits of popular songs.

## Tools Used
- Python (Pandas, Scikit-learn, Matplotlib, Seaborn)
- Google Colab
- KMeans, Logistic Regression, Decision Tree, KNN
- Association Rule Mining

## Team Contributions
- Aakash Kathirvel: K-Means Clustering, Association Analysis
- Chandhini K. M.: Data Preprocessing, KNN
- Matt Ferguson: Logistic Regression
- Milan Chaudhari: Decision Tree, Cost-Benefit Evaluation

## Report
- `Spotify_Popularity_Prediction_Report.docx` – Final report with analysis, insights, and managerial recommendations.

## Managerial Insights
- Focus on songs with high danceability, energy, and loudness.
- Use profit-based model selection when optimizing recommendation impact.
- Cluster-aware recommendations improve personalization.

