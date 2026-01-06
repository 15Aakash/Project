# **Cinema Ticket Sales Forecasting (2017–2018) using R Programming**

This project analyzes and forecasts daily cinema ticket sales using advanced time series forecasting methods. By examining historical trends in ticket revenue, we identified key patterns such as weekly seasonality, short-term spikes, and gradual long-term shifts in consumer behavior. A range of models—Time Series Regression, Exponential Smoothing (ETS), ARIMA, and an Ensemble Approach—were employed to generate robust forecasts.

The final model, a **Manual Ensemble Model (ARIMA + ETS)**, demonstrated strong predictive accuracy by capturing both seasonality and underlying trends. The 30-day operational forecast supports business planning for staffing, marketing, and inventory decisions in the entertainment sector.

## **Project Overview**
Ticket sales in the cinema industry fluctuate due to weekends, holidays, promotions, and film releases. Accurately forecasting these fluctuations helps optimize resources and improve revenue management. This project includes:

+ **Data Cleaning & Aggregation**: Duplicates were removed and missing values were handled using linear interpolation.

+ **Time Series Analysis**: Decomposition was used to visualize seasonal and trend components.

+ **Forecasting Models**:

    + **Time Series Regression**: Captures general trend and weekly patterns.

    + **ARIMA (manual & auto)**: Models autocorrelation and adjusts for seasonality.

    + **ETS (manual & auto)**: Considers additive/multiplicative trends and seasonal patterns.

    + **Ensemble Model**: Combines strengths of ARIMA and ETS for greater accuracy.

### **Key Findings**
+ The **Manual ARIMA(2,1,1)(2,1,1)** and **ETS(M,A,M)** models performed best individually.

+ An **ensemble approach** using equal weighting of ARIMA and ETS models improved forecast reliability.

+ The model effectively captured **weekly seasonal patterns** and **short-term demand spikes**.

+ A **30-day forecast** was produced, enabling informed decision-making for upcoming cinema operations.

### **Project Files**
+ **Data**: Cleaned daily cinema ticket sales dataset (cinemaTicket_Ref.csv)

+ **Scripts**: Full R code (Cinema Ticket Sales Forcasting.r) for preprocessing, modeling, and forecasting

+ **Results**: Accuracy metrics (MAPE), plots comparing fitted vs actual values, and future forecasts

### **Getting Started**
Clone this repository and run the R script to replicate the entire forecasting workflow. The code includes data preparation, model building, accuracy evaluation, and visualization.

### **Requirements**
+ **R version**: 4.0 or later

+ **Libraries Used:**

    + forecast

    + fable

    + feasts

    + ggplot2

    + tsibble

    + imputeTS

    + dplyr, tidyverse, lubridate

Ensure all required packages are installed before running the script.

### **Forecast Results**
+ A **validation forecast** compared actual sales with predicted values to evaluate model performance.

+ A **30-day operational forecast** was generated to simulate real-world application.

+ Forecast accuracy was assessed using **MAPE**, with ensemble models outperforming standalone models.

### **Conclusion**
This project showcases how time series modeling can be applied to real-world ticket sales data. The ensemble forecasting approach offers reliable predictions by balancing trend, seasonality, and randomness—making it valuable for decision-making in cinema operations, staffing, and promotions.

