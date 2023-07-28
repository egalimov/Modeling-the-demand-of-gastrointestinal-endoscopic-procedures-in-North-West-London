# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 12:53:19 2023

@author: EvgenyGalimov
"""



import pandas as pd
from datetime import datetime
import datetime
from fbprophet import Prophet
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
from fbprophet.diagnostics import cross_validation
import os
import shutil

# set max string display - to convert pandas series to string
pd.set_option("display.max_colwidth", 10000)

# set path
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/'

# load the file with parameters
params = pd.read_excel(path+'params2_5y_Prophet_2020oct.xlsx', sheet_name = 'params')






# Master function to perform prophet analysis and save the results
def run_prophet(path, folder, file, start_w, end_w, save_folder, test_data_points, forecast_period):
    # load the data
    data = pd.read_csv(path+folder+file+'.csv')

    # convert string to Timestamp and rename columns
    data['week_first_day']=pd.DatetimeIndex(data['week_first_day'])
    data=data.rename(columns={'week_first_day':'ds','n_visits':'y'})
        
    # copy data and limit start and end as in params table
    data2 = data[['ds','y']]
    data2_pc = data2[ (data2['ds']>=start_w) & (data2['ds']<=end_w) ]
    
    
    # plot original data and save it
    data2_pc['ds'] = pd.to_datetime(data2_pc['ds'])
    ax=data2_pc.set_index('ds').plot(figsize=(12,8))
    ax.set_ylabel('Weekly Number')
    ax.set_xlabel('Date')
    plt.savefig( path+save_folder+'___'+'1_original data.jpg', dpi=300, transparent  = True, format='jpg')

    
    # split data into train and test
    data2_pc.shape[0]
    train_pc = data2_pc.iloc[0:data2_pc.shape[0]-test_data_points,:]
    test_pc = data2_pc.iloc[data2_pc.shape[0]-test_data_points:data2_pc.shape[0],:]

    print(f"Number of weeks in train data: {len(train_pc)}")
    print(f"Number of weeks in test data: {len(test_pc)}")
    
    
    ### with train/test split 
    # train Prophet model
    p_mod_4=Prophet(interval_width=0.95)
    p_mod_4.fit(train_pc)
    
    # merge observed and forecast
    test_dates_pc = test_pc[['ds']]
    forecast4=p_mod_4.predict(test_dates_pc)
    forecast4[['ds','yhat','yhat_lower','yhat_upper']].tail()
    forecast4 = pd.merge(forecast4, data2_pc, how="left", on=["ds"])
    
    # get forecast metrics on the test period
    p_mod_4_test_metrics = pd.DataFrame({
           "MSE": [round(  mean_squared_error(forecast4['yhat'], forecast4['y']), 0)],
           "RMSE": [round(  mean_squared_error(forecast4['yhat'], forecast4['y'], squared = False), 0)],
           "MAPE": [round(  mean_absolute_percentage_error(forecast4['yhat'], forecast4['y']), 2)],
           "MAE": [round(  mean_absolute_error(forecast4['yhat'], forecast4['y']), 0)] })
    p_mod_4_test_metrics.to_csv(path+save_folder+'___'+'2_model1_metrics.csv')
    
    
    # train Prophet and predict using crossvalidation method
    p_mod_5=Prophet(interval_width=0.95)
    p_mod_5.fit(data2_pc)
    df_cv2 = cross_validation(p_mod_5, initial=str(len(train_pc)-1)+' W', period=str(test_data_points)+' W', horizon = str(test_data_points)+' W')
    
    p_mod_5.plot(df_cv2, uncertainty=True)
    plt.xticks(rotation=30)
    plt.xlabel("Date")
    plt.ylabel("Estimated visits per week")
    plt.text(df_cv2.iloc[0,0],df_cv2['y'].max(), "MAE: "+str(round(  mean_absolute_error(df_cv2['yhat'], df_cv2['y']), 0)), fontsize = 15)
    plt.savefig( path+save_folder+'___'+'3_model2_cv.jpg', dpi=300, transparent  = True, format='jpg')

    # get forecast metrics on the test period
    p_mod_5_test_metrics = pd.DataFrame({
           "MSE": [round(  mean_squared_error(df_cv2['yhat'], df_cv2['y']), 0)],
           "RMSE": [round(  mean_squared_error(df_cv2['yhat'], df_cv2['y'], squared = False), 0)],
           "MAPE": [round(  mean_absolute_percentage_error(df_cv2['yhat'], df_cv2['y']), 2)],
           "MAE": [round(  mean_absolute_error(df_cv2['yhat'], df_cv2['y']), 0)] })
    p_mod_5_test_metrics.to_csv(path+save_folder+'___'+'4_model2_metrics.csv')

    
    # make forecast for the next 5 years
    future_dates2 = p_mod_5.make_future_dataframe(periods=forecast_period,freq='MS')
    forecast5=p_mod_5.predict(future_dates2)
    forecast5 = pd.merge(forecast5, data2_pc, how="left", on=["ds"])

    # plot the forecast
    forecast5[['ds','yhat','yhat_lower','yhat_upper']].tail()
    p_mod_5.plot(forecast5, uncertainty=True)
    plt.text(df_cv2.iloc[0,0],df_cv2['y'].max(), "MAE: "+str(round(  mean_absolute_error(df_cv2['yhat'], df_cv2['y']), 0)), fontsize = 15)
    plt.savefig( path+save_folder+'___'+'5_model2_forecast.jpg', dpi=300, transparent  = True, format='jpg')
    
    # plot component plot    
    p_mod_5.plot_components(forecast5)
    plt.xticks(rotation=30)
    plt.savefig( path+save_folder+'___'+'6_model2_component_plot.jpg', dpi=300, transparent  = True, format='jpg')

    # save the forecast table
    forecast5.to_csv(path+save_folder+'___'+'7_model2_forecast.csv')



# error list
error_list = []

# iterate over all sites/procedures and get Prophet analysis using run_prophet master function
for k in range(0, params.shape[0]):
    #k=0
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
    
    # run master function to perform prophet analysis and save the results
    try: run_prophet(path, folder, file, start_w, end_w, save_folder, test_data_points, forecast_period)
    except: error_list.append(str(k)+': ' + str(ValueError) )





# copying files
if not os.path.exists(path+save_folder.split("/",1)[0]+'/1_pred_Prophet/0_all'):
    os.makedirs(path+save_folder.split("/",1)[0]+'/1_pred_Prophet/0_all')

files = os.listdir(path+save_folder.split("/",1)[0]+'/1_pred_Prophet/')
for file in files:
    if '5_model2' in file.lower():
       shutil.copy(path+save_folder.split("/",1)[0]+'/1_pred_Prophet/'+file, path+save_folder.split("/",1)[0]+'/1_pred_Prophet/0_all/'+file)
    if '1_original' in file.lower():
       shutil.copy(path+save_folder.split("/",1)[0]+'/1_pred_Prophet/'+file, path+save_folder.split("/",1)[0]+'/1_pred_Prophet/0_all/'+file)




























































































































