# Load Required Libraries
library(forecast)
library(tidyverse)
library(lubridate)
library(ggplot2)
library(tsibble)
library(fable)
library(feasts)
library(imputeTS)

# Set Working Directory
setwd("D:/VCU COURSE/FORECASTING METHODS/presentation final")

# Load the Dataset
CinemaSales.df <- read.csv("cinemaTicket_Ref.csv")

# Preprocess Data
# Convert the 'date' column to Date type and rename 'total_sales' to 'TotalSales' for consistency
CinemaSales.df <- CinemaSales.df %>% 
  dplyr::mutate(Date = as.Date(date)) %>% 
  dplyr::select(Date, TotalSales = total_sales)  

# Check for and handle duplicates
# Group data by Date and aggregate TotalSales by summing up values (if duplicates exist)
CinemaSales.df <- CinemaSales.df %>%
  group_by(Date) %>%  # Group by Date to identify duplicates
  summarise(TotalSales = sum(TotalSales, na.rm = TRUE)) %>%  # Sum sales for each unique date
  ungroup()  # Remove grouping for further processing

# Convert to tsibble
CinemaSales.tb <- CinemaSales.df %>%
  as_tsibble(index = Date)

# Handle missing dates and interpolate TotalSales
CinemaSales.tb <- CinemaSales.tb %>%
  complete(Date = seq.Date(min(Date), max(Date), by = "day")) %>%
  mutate(TotalSales = na_interpolation(TotalSales, option = "linear"))

# Partition the Data
CinemaSales.tb.train <- CinemaSales.tb %>%
  filter(Date <= as.Date("2018-08-31")) %>%
  as_tsibble(index = Date)  # Ensure it's a tsibble

CinemaSales.tb.validation <- CinemaSales.tb %>%
  filter(Date > as.Date("2018-08-31")) %>%
  as_tsibble(index = Date)  # Ensure it's a tsibble

# Visualize Training Data
# Time Series Plot
CinemaSales.tb.train %>%
  autoplot(TotalSales) +
  ggtitle("Cinema Ticket Sales - Training Data") +
  xlab("Date") +
  ylab("Total Sales")

# Decompose the Time Series Using STL
CinemaSales.tb.train.decomp <- CinemaSales.tb.train %>%
  model(STL(TotalSales ~ trend(window = 7))) %>%
  components()

# Visualize Decomposed Components
autoplot(CinemaSales.tb.train.decomp) +
  ggtitle("Decomposition of Cinema Ticket Sales") +
  xlab("Date")

#The trend shows an initial sharp increase in cinema ticket sales around March-April,followed by a gradual decline. The seasonality exhibits a strong weekly pattern with consistent fluctuations, reflecting periodic demand.

## Fit a regression model to the training data with trend and seasonality terms
fit_CinemaSales <- CinemaSales.tb.train %>%
  model(TSLM(TotalSales ~ trend() + season()))

# Summarize the model fit
fit_CinemaSales %>% report()

# Regression Model Summary:
# The model identifies a weak upward trend (not significant) and significant seasonal patterns for weeks 3, 4, 5, and 7.
# Adjusted R-squared (0.1841) suggests a modest fit, indicating room for improvement in capturing variability.

## Compare the fit to the training data
fit_CinemaSales %>%
  augment() %>%
  ggplot(aes(x = Date)) +
  geom_line(aes(y = TotalSales, colour = "Data")) +
  geom_line(aes(y = .fitted, colour = "Fitted")) +
  scale_colour_manual(
    values = c(Data = "black", Fitted = "green3")
  ) +
  guides(colour = guide_legend(title = "Series")) +
  ggtitle("Comparison of Data and Fitted Values") +
  xlab("Date") +
  ylab("Total Sales")

## Forecast the validation period
fc_CinemaSales <- fit_CinemaSales %>%
  forecast(new_data = CinemaSales.tb.validation)

# Plot the forecast and prediction intervals
fc_CinemaSales %>%
  autoplot(CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "blue") +
  ggtitle("Cinema Ticket Sales Forecast") +
  xlab("Date") +
  ylab("Total Sales") +
  guides(colour = guide_legend(title = "Series"))

## Step 1: Check Stationarity and Differencing Requirements
# Determine the number of regular and seasonal differences needed
CinemaSales.tb.train %>% features(TotalSales, unitroot_ndiffs)  # Regular differencing(d = 0)
CinemaSales.tb.train %>% features(TotalSales, unitroot_nsdiffs) # Seasonal differencing(D = 1)

## Step 2: Start with a Basic ARIMA Model
# Fit a basic ARIMA model with minimal differencing
ARIMAA.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(0,0,0) + PDQ(0,1,0)))  
report(ARIMAA.fit) #AIC=8692.22
# Check residuals for autocorrelation
augment(ARIMAA.fit) %>% gg_tsdisplay(.resid, plot_type = "partial") 

ARIMA0.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(0,1,0) + PDQ(0,1,0)))  
report(ARIMA0.fit) # AIC=8587.62 :  provides a baseline for model comparison. 
# Check residuals for autocorrelation
augment(ARIMA0.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

ARIMA0a.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(0,1,0) + PDQ(0,1,1)))  
report(ARIMA0a.fit) # AIC=8532.76 :  provides a baseline for model comparison. 
# Check residuals for autocorrelation
augment(ARIMA0a.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

ARIMA0b.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(0,1,0) + PDQ(1,1,1)))  
report(ARIMA0b.fit) # AIC=8534.22 :  provides a baseline for model comparison. 
# Check residuals for autocorrelation
augment(ARIMA0b.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

## Step 3: Adjust ARIMA Parameters Using ACF/PACF Insights
# Refine the ARIMA model parameters (p, q, P, Q) based on patterns in the residual ACF and PACF.
# Incorporating a seasonal autoregressive component (P = 1) to capture seasonal dependencies.
ARIMA1.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(1,1,1) + PDQ(0,1,1)))  # Seasonal AR term
report(ARIMA1.fit)  # AIC = 8510.5
augment(ARIMA1.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

ARIMA2.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(0,1,1) + PDQ(0,1,1)))  # Seasonal AR term
report(ARIMA2.fit)  # AIC = 8512.69
augment(ARIMA2.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

ARIMA3.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales ~ pdq(1,1,0) + PDQ(0,1,1)))  # Seasonal AR term
report(ARIMA3.fit)  # AIC = 8522.59
augment(ARIMA3.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

# Since the spikes for both the p,d,q versions are on 11, we are going to consider the lowest AIC
# Not going to consider ARIMA3 because there's a spike in 2

## Step 4: Select the Best Model Based on AIC
# Compare the AIC values from all fitted models
# So ARIMA1.fit has the lowest AIC and is the selected model
## Step 5: Validate Residuals for Selected Model
augment(ARIMA1.fit) %>% gg_tsdisplay(.resid, plot_type = "partial")

## Step 6: Compare the Fit to the Training Data
ARIMA1.fit %>%
  augment() %>%
  ggplot(aes(x = Date)) +
  geom_line(aes(y = TotalSales, colour = "Data")) +
  geom_line(aes(y = .fitted, colour = "Fitted")) +
  scale_colour_manual(
    values = c(Data = "black", Fitted = "green3")
 ) +
  guides(colour = guide_legend(title = "Series")) +
  ggtitle("Comparison of Data and Fitted Values") +
  xlab("Date") +
  ylab("Total Sales")


## Step 7: Forecast the Validation Period
fc_CinemaSales <- ARIMA1.fit %>%
  forecast(new_data = CinemaSales.tb.validation) 

# Plot forecast with prediction intervals
fc_CinemaSales %>%
  autoplot(CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "blue") +
  ggtitle("Cinema Ticket Sales Forecast") +
  xlab("Date") +
  ylab("Total Sales")

## Use auto.arima() to fit the best ARIMA model
ARIMAauto.fit <- CinemaSales.tb.train %>%
  model(ARIMA(TotalSales))

report(ARIMAauto.fit) #AIC is coming out to be 8551.34


# Create a plot to compare the auto-fitted model to the training data
ARIMAauto.fit %>%
  augment() %>%
  ggplot(aes(x = Date)) +
  geom_line(aes(y = TotalSales, colour = "Data")) +
  geom_line(aes(y = .fitted, colour = "Fitted")) +
  scale_colour_manual(
    values = c(Data = "black", Fitted = "green3")) +
  guides(colour = guide_legend(title = "Series")) +
  ggtitle("Comparison of Data and Auto-Fitted Values") +
  xlab("Date") +
  ylab("Total Sales")

# Forecast using the auto-fitted model
fc_CinemaSales_auto <- ARIMAauto.fit %>%
  forecast(h = nrow(CinemaSales.tb.validation))

# Plot the auto-fitted forecast
fc_CinemaSales_auto %>%
  autoplot(CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "blue") +
  ggtitle("Cinema Ticket Sales Auto-Fitted Forecast") +
  xlab("Date") +
  ylab("Total Sales") +
  guides(colour = guide_legend(title = "Series"))

## Fit an Exponential Smoothing Model

# Taking into account the trend and seasonality in the data:
# Residuals appear consistent, starting with "A" for the error component while exploring "M" for robustness.
# The trend shows an early rise followed by a gradual decline, suggesting an "A" (additive) trend component.
# The seasonal pattern remains stable with weekly variations, initially using "A" but also testing "M" (multiplicative).


# Fit the recommended ETS models

# Model 1: ETS(ANN) - Additive error, No trend, No seasonality
ets_manu_1 <- CinemaSales.tb.train %>% 
  model(ETS(TotalSales ~ error("A") + trend("A") + season("M")))  
report(ets_manu_1)  # AIC = 9327.669

# Model 2: ETS(ANA) - Additive error, No trend, Additive seasonality
ets_manu_2 <- CinemaSales.tb.train %>% 
  model(ETS(TotalSales ~ error("A") + trend("A") + season("A")))  
report(ets_manu_2)  # AIC = 9362.465

# Model 3: ETS(ANM) - Additive error, No trend, Multiplicative seasonality
ets_manu_3 <- CinemaSales.tb.train %>% 
  model(ETS(TotalSales ~ error("M") + trend("A") + season("M")))  
report(ets_manu_3)  # AIC = 9266.055

# Model 4: ETS(ANM) - Additive error, No trend, Multiplicative seasonality
ets_manu_4 <- CinemaSales.tb.train %>% 
  model(ETS(TotalSales ~ error("M") + trend("A") + season("A")))  
report(ets_manu_4)  # AIC = 9657.732

# Comment:
# Among the three ETS models, Model 3 (ETS(ANM) with multiplicative seasonality and additive trend) has the lowest AIC (9323.473),
# making it the best candidate for forecasting.

## Create a plot to compare the fit to the training data
ets_manu_3 %>%
  augment() %>%
  ggplot(aes(x = Date)) +
  geom_line(aes(y = TotalSales, colour = "Data")) +
  geom_line(aes(y = .fitted, colour = "Fitted")) +
  scale_colour_manual(
    values = c(Data = "black", Fitted = "green3")) +
  guides(colour = guide_legend(title = "Series")) +
  ggtitle("Comparison of Data and Fitted Values for ETS Model") +
  xlab("Date") +
  ylab("Total Sales")

## Forecast the Validation Period
fc_CinemaSales <- ets_manu_3 %>%
  forecast(h = nrow(CinemaSales.tb.validation))

# Plot the forecast with prediction intervals
fc_CinemaSales %>%
  autoplot(CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "orange") +
  ggtitle("Cinema Ticket Sales Forecast (ETS Model)") +
  xlab("Date") +
  ylab("Total Sales")

## Auto ETS

# Automatically fit the best ETS model to the training data
ets_auto <- CinemaSales.tb.train %>%
  model(ETS(TotalSales))  

report(ets_auto)

# Comment:
# The automatic ETS model selected is ETS(M,A,M) - Multiplicative error, Additive trend, and Multiplicative seasonality.
# This model achieves an AIC of 9266.055, making it competitive with the manually tuned ETS models.

# Create a plot to compare the fit to the training data
ets_auto %>%
  augment() %>%
  ggplot(aes(x = Date)) +
  geom_line(aes(y = TotalSales, colour = "Data")) +
  geom_line(aes(y = .fitted, colour = "Fitted")) +
  scale_colour_manual(
    values = c(Data = "black", Fitted = "green3")) +
  guides(colour = guide_legend(title = "Series")) +
  ggtitle("Comparison of Data and Fitted Values for Auto ETS Model") +
  xlab("Date") +
  ylab("Total Sales")

# Forecast using the auto ETS model
fc_CinemaSales_auto <- ets_auto %>%
  forecast(h = nrow(CinemaSales.tb.validation))

# Plot the auto ETS forecast
fc_CinemaSales_auto %>%
  autoplot(CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "blue") +
  ggtitle("Cinema Ticket Sales Auto ETS Forecast") +
  xlab("Date") +
  ylab("Total Sales") +
  guides(colour = guide_legend(title = "Series"))

## Model Accuracy
# Fit all models to training data
all.models.fit <- CinemaSales.tb.train %>%
  model(
    arima_manual = ARIMA(TotalSales ~ pdq(2,1,1) + PDQ(2,1,1)),  # Best manual ARIMA model
    arima_auto = ARIMA(TotalSales),  # Auto ARIMA model
    ts_reg = TSLM(TotalSales ~ trend() + season()),  # Regression model
    ets_manual = ETS(TotalSales ~ error("A") + trend("N") + season("M")),  # Best manual ETS model
    ets_auto = ETS(TotalSales),  # Auto ETS model
    naive = NAIVE(TotalSales),  # Naive model
    snaive = SNAIVE(TotalSales)  # Seasonal naive model
  )

# Forecast for the validation period
all.models.pred <- all.models.fit %>% forecast(new_data = CinemaSales.tb.validation)

# Evaluate accuracy
accuracy_results <- all.models.pred %>%
  accuracy(CinemaSales.tb.validation) %>%
  arrange(MAPE)  # Sort by MAPE for comparison

# Print the accuracy evaluation results
print(accuracy_results)

## Step 9: Ensemble - Manual ARIMA and ETS Models

# Create an ensemble model using the best manual ARIMA and ETS models
ensemble_model <- CinemaSales.tb.train %>%
  model(
    arima_manual = ARIMA(TotalSales ~ pdq(2,1,1) + PDQ(2,1,1)),  # Best manual ARIMA model
    ets_manual = ETS(TotalSales ~ error("A") + trend("N") + season("M"))  # Best manual ETS model
  ) %>%
  mutate(Ensemble = (arima_manual + ets_manual) / 2)  # Equal weighting for ARIMA and ETS models

# This step creates an ensemble model by averaging predictions from the best manual ARIMA model (ARIMA(0,1,1)(1,0,0))
# and the best manual ETS model (ETS(ANM)). This approach combines the strengths of both models to improve forecast accuracy.


# Forecast for validation period
ensemble_forecast <- ensemble_model %>% forecast(new_data = CinemaSales.tb.validation)

# Evaluate ensemble accuracy
ensemble_accuracy <- ensemble_forecast %>%
accuracy(CinemaSales.tb.validation)
# Display ensemble accuracy
print(ensemble_accuracy)

## Step 11: Plot Ensemble Forecast
autoplot(ensemble_forecast, CinemaSales.tb.train) +
  autolayer(CinemaSales.tb.validation, colour = "blue") +
  ggtitle("Ensemble Forecast of Cinema Ticket Sales") +
  xlab("Date") +
  ylab("Total Sales") +
  guides(colour = guide_legend(title = "Series"))

# Step 12: Operational Forecast :

# Forecast for the next 30 days using the ARIMA manual model
arima_manual_forecast_30days <- all.models.fit %>%
  select(arima_manual) %>%  # Select the ARIMA manual model
  forecast(h = 30)  # Forecasting for the next 30 days

# Plot the 30-day forecast with historical data
autoplot(arima_manual_forecast_30days, CinemaSales.tb.train) +
  ggtitle("30-Day Forecast of Cinema Ticket Sales (ARIMA Manual Model)") +
  xlab("Date") +
  ylab("Total Sales") +
  guides(colour = guide_legend(title = "Series")) +
  theme_minimal()

# Plot the forecast with prediction intervals
arima_manual_forecast_30days %>%
  autoplot() +
  ggtitle("30-Day Forecast with Prediction Intervals (ARIMA Manual Model)") +
  xlab("Date") +
  ylab("Total Sales") +
  theme_minimal()

# Tabulate forecast values  
forecast_table_arima <- arima_manual_forecast_30days %>%
  as_tibble()  # Convert to a tibble for easier viewing

# Print the forecast table
print(forecast_table_arima)

# Evaluate ARIMA manual model accuracy
arima_manual_accuracy <- arima_manual_forecast_30days %>%
  accuracy(CinemaSales.tb.validation)

# Print accuracy results
print(arima_manual_accuracy)

