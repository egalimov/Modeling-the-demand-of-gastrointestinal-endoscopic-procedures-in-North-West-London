# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 12:53:19 2023

@author: EvgenyGalimov
"""


import itertools
import pandas as pd
from datetime import datetime
import datetime
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
import os
import shutil




# set max string display - to convert pandas series to string
pd.set_option("display.max_colwidth", 10000)

# set path
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/'

folder = 'Results/0_ChelWest/'
file = '0_CW_Colonoscopy_weekly_counts'


# load the file with parameters
params = pd.read_excel(path+'params2_5y_Sarima_2020oct.xlsx', sheet_name = 'params')



# Master function to perform SARIMA analysis and save the results
def run_sarima(path, folder, file, start_w, end_w, save_folder, test_data_points, forecast_period):
    # load the data
    data = pd.read_csv(path+folder+file+'.csv')
    
    # convert string to Timestamp and rename columns    
    data['week_first_day']=pd.DatetimeIndex(data['week_first_day'])
    data=data.rename(columns={'week_first_day':'ds','n_visits':'y'})

    # copy data and limit start and end as in params table        
    data2 = data[['ds','y']]
    data2_pc = data2[ (data2['ds']>=start_w) & (data2['ds']<=end_w) ]
    
    # plot original data and save it   
    ax=data2_pc.set_index('ds').plot(figsize=(12,8))
    ax.set_ylabel('Weekly Number')
    ax.set_xlabel('Date')
    plt.savefig( path+save_folder+'___'+'1_original data.jpg', dpi=300, transparent  = True, format='jpg')
    data2_pc = data2_pc.set_index('ds')

    
    # split data into train and test
    data2_pc.shape[0]
    train_pc = data2_pc.iloc[0:data2_pc.shape[0]-test_data_points,:]
    test_pc = data2_pc.iloc[data2_pc.shape[0]-test_data_points:data2_pc.shape[0],:]

    print(f"Number of weeks in train data: {len(train_pc)}")
    print(f"Number of weeks in test data: {len(test_pc)}")
    
    
    # with train/test split  - GRID SEARCH for sarima parameters
    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
    print('Examples of parameter combinations for Seasonal ARIMA...')
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
    print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
    print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))
    
    # df with various SARIMA parameters and performnce
    models = pd.DataFrame(columns=['Trend elements', 'Seasonal elements', 'AIC', 'MAE'])
    # iterate over Sarima parameters specified in pdq and seasonal_pdq
    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                # define the model
                mod = sm.tsa.statespace.SARIMAX(train_pc,
                        order=param,
                        seasonal_order=param_seasonal,
                        enforce_stationarity=False,
                        enforce_invertibility=False)
    
                results = mod.fit()
                results.summary()
                
                # get prediction
                pred = results.get_prediction(start = test_pc.index[0], end = test_pc.index[-1], dynamic=True)
                pred_ci = pred.conf_int()
                pred_ci['yhat'] = pred.predicted_mean
                pred_ci = pd.merge(pred_ci, data2_pc, how="left", left_index=True, right_index=True)

                # add the results to the df to compare various model with hyperparameters               
                models = models.append(pd.Series([param,param_seasonal,results.aic, mean_absolute_error(pred_ci['yhat'], pred_ci['y'])], index=['Trend elements', 'Seasonal elements', 'AIC', 'MAE']), ignore_index=True)
    
                print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
            except:
                continue
    
    # sort df with performance metrics in ascending order so the first model is the best
    models = models.sort_values(by=['MAE'], ascending = [True])
    models.to_csv(path+save_folder+'___'+'8_models_list.csv')


    # run the best model (parameters are extracted from models df)
    mod_2 = sm.tsa.statespace.SARIMAX(train_pc,
                                order=(models.iloc[0,0][0], models.iloc[0,0][1], models.iloc[0,0][2]),
                                seasonal_order=(models.iloc[0,1][0], models.iloc[0,1][1], models.iloc[0,1][2], models.iloc[0,1][3]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
    
    # fit the model and save the output
    results_2 = mod_2.fit()
    print(results_2.summary().tables[1])
    with open(path+save_folder+'___'+'9_best_model_summary.txt', 'w') as fh:
        fh.write(results_2.summary().as_text())    
    
    # calculate the performance metrics for the model on test data
    pred_2 = results_2.get_prediction(start = test_pc.index[0], end = test_pc.index[-1], dynamic=True)
    pred_ci_2 = pred_2.conf_int()
    
    pred_ci_2['yhat'] = pred_2.predicted_mean
    pred_ci_2 = pd.merge(pred_ci_2, data2_pc, how="left", left_index=True, right_index=True)
    
    
    s_mod_2_test_metrics = pd.DataFrame({
           "MSE": [round(  mean_squared_error(pred_ci_2['yhat'], pred_ci_2['y']), 0)],
           "RMSE": [round(  mean_squared_error(pred_ci_2['yhat'], pred_ci_2['y'], squared = False), 0)],
           "MAPE": [round(  mean_absolute_percentage_error(pred_ci_2['yhat'], pred_ci_2['y']), 2)],
           "MAE": [round(  mean_absolute_error(pred_ci_2['yhat'], pred_ci_2['y']), 0)] })
    # save the performance metrics
    s_mod_2_test_metrics.to_csv(path+save_folder+'___'+'2_model1_metrics.csv')
    
    
    # plot the forecast for the test period
    ax = data2_pc[train_pc.index[0]:].plot(label='observed',linewidth=2)
    pred_2.predicted_mean.plot(ax=ax, label='Prediction', alpha=.7, figsize=(10, 7), linewidth=2)
    ax.fill_between(pred_ci_2.index,pred_ci_2.iloc[:, 0],pred_ci_2.iloc[:, 1], color='k', alpha=.2)
    plt.legend(fontsize=14, loc="upper center")
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Estimated visits per week", fontsize=12)
    plt.text(train_pc.index[0], train_pc['y'].max(), "MAE: "+str(round(  mean_absolute_error(pred_ci_2['yhat'], pred_ci_2['y']), 0)), fontsize = 12)
    plt.savefig( path+save_folder+'___'+'3_model1_prediction.jpg', dpi=300, transparent  = True, format='jpg')


    # make forecast for next 5 years
    forecast_start0 = test_pc.index[0]
    forecast_end0 = forecast_start0 + relativedelta(months=+forecast_period+round(test_data_points/4.345, 0))
    pred2_2 = results_2.get_prediction(start = forecast_start0, end = forecast_end0, dynamic=True)
    pred_ci_22 = pred2_2.conf_int()
    pred_ci_22['yhat'] = pred2_2.predicted_mean
    pred_ci_22 = pd.concat([pred_ci_22, data2_pc], axis=1, join="outer")
    pred_ci_22.to_csv(path+save_folder+'___'+'4_model1_forecast.csv')

    # plot the forecast
    ax = data2_pc[train_pc.index[0]:].plot(label='observed',linewidth=2)
    pred2_2.predicted_mean.plot(ax=ax, label='Prediction', alpha=.7, figsize=(10, 15))
    ax.fill_between(pred_ci_22.index,pred_ci_22.iloc[:, 0],pred_ci_22.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel("Estimated visits per week", fontsize=14)
    plt.text(train_pc.index[0], train_pc['y'].max(), "MAE: "+str(round(  mean_absolute_error(pred_ci_2['yhat'], pred_ci_2['y']), 0)), fontsize = 12)
    plt.legend(fontsize=12, loc="upper center")
    plt.savefig( path+save_folder+'___'+'5_model1_forecast.jpg', dpi=300, transparent  = True, format='jpg')
    
    
    # use whole period for training
    # plot forecast for the best model for 3 years
    # run the best model
    mod_2_full = sm.tsa.statespace.SARIMAX(data2_pc,
                                order=(models.iloc[0,0][0], models.iloc[0,0][1], models.iloc[0,0][2]),
                                seasonal_order=(models.iloc[0,1][0], models.iloc[0,1][1], models.iloc[0,1][2], models.iloc[0,1][3]),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
    results_2_full = mod_2_full.fit()
    print(results_2_full.summary().tables[1])    
    
    forecast_start = data2_pc.index[-1] + datetime.timedelta(days=7)
    forecast_end = forecast_start + relativedelta(months=+forecast_period)

    # get table with the forecast
    pred3 = results_2_full.get_prediction(start = forecast_start, end = forecast_end, dynamic=True)
    pred_ci_3 = pred3.conf_int()
    pred_ci_3['yhat'] = pred3.predicted_mean
    pred_ci_3 = pd.concat([pred_ci_3, data2_pc], axis=1, join="outer")
    pred_ci_3.to_csv(path+save_folder+'___'+'6_model2_forecast.csv')

    # plot the forecast
    ax = data2_pc[train_pc.index[0]:].plot(label='observed',linewidth=2)
    pred3.predicted_mean.plot(ax=ax, label='Prediction', alpha=.7, figsize=(10, 15))
    ax.fill_between(pred_ci_3.index,pred_ci_3.iloc[:, 0],pred_ci_3.iloc[:, 1], color='k', alpha=.2)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel("Estimated visits per week", fontsize=14)
    plt.legend(fontsize=12, loc="upper center")
    plt.savefig( path+save_folder+'___'+'7_model2_forecast.jpg', dpi=300, transparent  = True, format='jpg')
    
    
    
    
    
# error list
error_list = []

# iterate over all sites/procedures get SARIMA analysis using run_sarima master function
for k in range(0, params.shape[0]):
    k=0
    # load parameters from param file
    folder = params.iloc[k][['folder']].to_string(index = False)
    file = params.iloc[k][['file']].to_string(index = False)
    start_w = params.iloc[k][['start_w']].to_string(index = False)
    end_w = params.iloc[k][['end_w']].to_string(index = False)
    save_folder = params.iloc[k][['save_folder']].to_string(index = False)
    test_data_points = int(params.iloc[k][['test_data_points']])
    forecast_period = int(params.iloc[k][['forecast_period']])
    
    # create folder for saving
    if not os.path.exists(path+save_folder):
        os.makedirs(path+save_folder)
    # run master function to perform SARIMA analysis and save the results    
    try: run_sarima(path, folder, file, start_w, end_w, save_folder, test_data_points, forecast_period)
    except: error_list.append(str(k)+': ' + str(ValueError) )


# copying files
if not os.path.exists(path+save_folder.split("/",1)[0]+'/2_pred_Sarima/0_all'):
    os.makedirs(path+save_folder.split("/",1)[0]+'/2_pred_Sarima/0_all')

files = os.listdir(path+save_folder.split("/",1)[0]+'/2_pred_Sarima/')
for file in files:
    if '5_model1' in file.lower():
       shutil.copy(path+save_folder.split("/",1)[0]+'/2_pred_Sarima/'+file, path+save_folder.split("/",1)[0]+'/2_pred_Sarima/0_all/'+file)
    if '7_model2' in file.lower():
       shutil.copy(path+save_folder.split("/",1)[0]+'/2_pred_Sarima/'+file, path+save_folder.split("/",1)[0]+'/2_pred_Sarima/0_all/'+file)


    
    
    
    
    
    
    
    
    















































































































