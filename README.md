# Modelling the demand of gastrointestinal endoscopic procedures in North West London


## Project Description
This repository contains the code for forecasting the the number of weekly endoscopies (and points reflecting the staff capacit required for endoscopy) for the next 5 years (2023-2027) based on the up to 10 years of historical data obtained from 6 providers in North West London. 3 different approaches were used for the modelling: Prophet, SARIMA and Exponential smoothing. The forecasts of best models from chosen sites/procedures were combined to predict the demand for each provider or the whole North West London. 


## Data sources
The data were received from the following providers: 
	* Chelsea and Westminster NHS Foundation Trust 
	* Imperial College Healthcare NHS Trust 
	* London North West Healthcare NHS Trust
	* The Hillingdon Hospitals NHS Foundation Trust
	* Healthshare
	* NHS bowel cancer screening programme (BCSP)


## Data
The data contain the date, procedure codes, procedure categories, patients numbers, points for each procedure for each of 5 datasets: referrals, rebookings, emergency, surveilance, removals.     


## About the repository
As mentioned above, the data from 6 sources were analysed.  

The repository contains scripts for the following steps:
1) Data preprocessing, checks for missing data, combining information about endoscopies from 5 tabs (referrals, rebookings, emergency, surveilance, removals) into one dataset.  Script names for each of 6 providers: 
	* step1_ChelWest.py
	* step1_Hillingdon.py
	* step1_Imperial.py
	* step1_LMW.py
	* step1_BCSP.py
	* step1_Healthshare.py

The output datasets with names ending 'combined.csv' are used in the next step 2.


2) Creating time series datasets with endoscopy counts agrregated per week. The counts for each week were calculated as: referrals + rebookings + emergency + surveilance - removals. 
Script names for each of 6 providers: 
	* step2_timeSeries_ChelWest.py
	* step2_timeSeries_Hillingdon.py
	* step2_timeSeries_Imperial.py
	* step2_timeSeries_LMW.py
	* step2_timeSeries_BCSP.py
	* step2_timeSeries_Healthshare.py

The scripts outputs for each site from 6 providers included: plot with original time series, time series with weekly data which are saved in files endinbg weekly_counts.csv and used in the step 3, and plots for these time series. 


3) Performing 5 year forecasting for each site from 6 providers using Prophet, SARIMA, Exponential smoothing models. The parameters defining start and end dates for each time series as well as forecasting period and saving location were loaded from params2_5y_Prophet_2020oct.xlsx, params2_5y_Sarima_2020oct.xlsx, params2_5y_ES_2020oct.xlsx tables for Prophet, SARIMA and Exponential models accordingly. In each case for SARIMA model, grid search for the best model was performed where p,d,q and seasonal p,d,q could be 0 or 1, with seasonal parameter set monthly. In the case of exponential smoothing, the grid search was performed among models where trend, seasonality types could be none, additive, multiplicative, error models could be additive and multiplicative, damped trend could be false or true, and seasonal parameter was set monthly. The best model was chosed based on the lowest MAE on the test period. 

Script names for Prophet, SARIMA and Exponential smooting models, accordingly: 
	* step3_prophet_cycle.py
	* step3_sarima_cycle.py
	* step3_es_cycle.py

The scripts outputs for each site from 6 providers: plot with original time series, plot with the 5 year forcast with displayed MAE for the test period, file with performance metrics (MSE, RMSE, MAPE, MAE), csv file with original data and forecast results. The csv files (ending: Prophet - 7_model2_forecast.csv, SARIMA - 4_model1_forecast.csv, Exponential smooting - 4_model1_forecast.csv) are used in the step 4. 


4) Combining the forecasts from different providers for different procedure types (gastroscopy, colonoscopy etc) to plot the forecast total number of procedures for next 5 years. The script uses forecasts generated at the previous step and chooses the model with lowest MAE on the test among Prophet, best SARIMA and best Exponential smooting model. 
The sites and saving locations are defined in the paramneter file params2_5y_2020oct.xslx. 

Script name is step4_get_sum_of_forecasts.py and the output for each provider/procedure type includes: plot of the sum of observed counts and sum of forecasts, file with of observed counts, file with sum of forecasts. It also outpouts similar files for forecasting the number of points per week (different types of procedures require different numbers of points depending on number of staff involved). The average number of points for each procedure/site are defined in params2_5y_2020oct.xslx.




## Requirements
The work was done using:
Python 3.7.16	
	Packages:
	* Fbprophet 0.7.1
	* Matplotlib 3.2.2
	* Numpy	1.21.6
	* Pandas 1.2.3
	* Sklearn 1.0.2
	* Statsmodels 0.13.5



## Authors
- Evgeniy Galimov |   e.r.galimov@gmail.com   |  https://www.linkedin.com/in/evgeniygalimov


## License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).


































