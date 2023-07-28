# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 11:24:34 2023

@author: EvgenyGalimov
"""


#import warnings
#import itertools
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
# import datetime
#import matplotlib.dates as mdates
#from fbprophet import Prophet
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import copy
#import statsmodels.api as sm
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
#from statsmodels.tsa.stattools import adfuller
#from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
#from fbprophet.diagnostics import cross_validation
#from pandas import Timestamp
import os
pd.set_option("display.max_colwidth", 10000)
import math
import shutil
from sklearn.linear_model import LinearRegression



# set the path for saving the outputs
path0 = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/'
path = path0 + '0_oct2020_5y_forecast/'


# copy files with from all 3 types of models
if not os.path.exists(path+'4_1-3_mod_results'+'/'):
    # If it doesn't exist, create it
    os.makedirs(path+'4_1-3_mod_results'+'/')

mod_folders = [path+'1_pred_Prophet'+'/0_all',path+'2_pred_Sarima'+'/0_all',path+'3_pred_ES'+'/0_all']
for i in mod_folders:
    files = os.listdir(i)
    for file in files:
        #i = path+'1_pred_Prophet'+'/0_all'
        #i=path+'3_pred_ES'+'/0_all'
        if i.find('Prophet') != -1:
            if '5_model2' in file.lower():
                shutil.copy(i+'/'+file, path+'4_1-3_mod_results'+'/'+file[:-4]+'_P.jpg')
        if i.find('Sarima') != -1:
            if '5_model1' in file.lower():
                shutil.copy(i+'/'+file, path+'4_1-3_mod_results'+'/'+file[:-4]+'_S.jpg')
        if i.find('pred_ES') != -1:
            if '5_model1' in file.lower():
                shutil.copy(i+'/'+file, path+'4_1-3_mod_results'+'/'+file[:-4]+'_E.jpg')



# list of names of param files for Prophet, Sarima, ES. They are used in plot_forecast function
param_files_list = ['params2_5y_Prophet_2020oct.xlsx', 'params2_5y_Sarima_2020oct.xlsx', 'params2_5y_ES_2020oct.xlsx']




# create a dictionary of dictionaries with lists of indexes from Params
    # for each trust and all of the them together split by type of endoscopy

# list of numbers in param files for colonoscopy (c), gastroscopy (g), sigmoidoscopy(s), all 3, ercp and CTC (CTC will not be used) 
params = pd.read_excel(path0+'params2_5y_Prophet_2020oct.xlsx', sheet_name = 'params')

trusts = {'all_trusts': {'c':[], 'g':[], 's':[], 's_c':[],'s_c_all':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'ChelWest':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'Hillingdon':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'Imperial':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'LNW':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'BCSP':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]},
          'HealthShare':{'c':[], 'g':[], 's':[], 's_c':[], 'cgs':[], 'ecrp':[], 'All':[]}, }

# function for repeated 'if conditions'
def repeated_if(i, params, trusts, tag):
    trusts['all_trusts'][tag].append(params.index[i])
    if (i>=0)&(i<10):
        trusts['ChelWest'][tag].append(params.index[i])
    if (i>=10)&(i<18):
        trusts['Hillingdon'][tag].append(params.index[i])
    if (i>=18)&(i<24):
        trusts['Imperial'][tag].append(params.index[i])
    if (i>=24)&(i<36):
        trusts['LNW'][tag].append(params.index[i])
    if (i>=36)&(i<40):
        trusts['BCSP'][tag].append(params.index[i])
    if (i>=40)&(i<54):
        trusts['HealthShare'][tag].append(params.index[i])
    
    return trusts


# cycle to populate the dictionary
for i in range(0, params.shape[0]):
    trusts = repeated_if(i, params, trusts, 'All')

    if (params.iloc[i][['save_folder']].to_string(index = False).find('_Colonoscopy') != -1) & (params.iloc[i][['save_folder']].to_string(index = False).find('_Colonoscopy_') == -1):
        trusts['all_trusts']['s_c_all'].append(params.index[i])
        trusts = repeated_if(i, params, trusts, 'c')
        
    if params.iloc[i][['save_folder']].to_string(index = False).find('_Gastroscopy') != -1:
        trusts = repeated_if(i, params, trusts, 'g')
        
    if params.iloc[i][['save_folder']].to_string(index = False).find('_OGD_and_Colon') != -1:
        trusts = repeated_if(i, params, trusts, 'cgs')
            
    if params.iloc[i][['save_folder']].to_string(index = False).find('_ERCP') != -1:
        trusts = repeated_if(i, params, trusts, 'ecrp')
        
    if params.iloc[i][['save_folder']].to_string(index = False).find('_Colonoscopy_and_Flexible_Sigmoidoscopy') != -1:
        trusts['all_trusts']['s_c_all'].append(params.index[i])
        trusts = repeated_if(i, params, trusts, 's_c')

    if (params.iloc[i][['save_folder']].to_string(index = False).find('_Flexible_Sigmoidoscopy') != -1) & (params.iloc[i][['save_folder']].to_string(index = False).find('and_Flexible_Sigmoidoscopy') == -1):
        trusts['all_trusts']['s_c_all'].append(params.index[i])
        trusts = repeated_if(i, params, trusts, 's')

    if (params.iloc[i][['save_folder']].to_string(index = False).find('_Flexible Sigmoidoscopy') != -1):
        trusts['all_trusts']['s_c_all'].append(params.index[i])
        trusts = repeated_if(i, params, trusts, 's')
        
   


# Load table with parameters and populate column with best chosen model (from PROPHET, SARIMA, ES)
model_choice = pd.read_excel(path0+'params2_5y_2020oct.xlsx', sheet_name = 'params')

# function to add 0 to numbers below 10 in the column defining the number of the site for endoscopy            
def add_0(a):
    if a<10:
        out = '0'+str(a)
    if a>=10:
        out = str(a)    
    return out
model_choice['Prefix2'] = model_choice['Prefix'].map(add_0)

# set high number for columns with MAE for Prophet, Sarima, ES: P_metric, S_metric, E_metric  
model_choice['P_metric'] = 10000
model_choice['S_metric'] = 10000
model_choice['E_metric'] = 10000
# set default N for the best model choice
model_choice['Best_model_metric'] = 'N'


# add model name automatically chosen based on a metric
#for i in range(0, model_choice.shape[0]):

# function to get metric from a saved file based on param table
def get_metric(i, model_folder, mod_ext, metric):
    try: 
        p_temp = pd.read_csv(path+model_folder+model_choice.iloc[i][['Prefix2']].to_string(index = False)+'_'+model_choice.iloc[i][['file']].to_string(index = False)[:-13]+mod_ext)
        m = float(p_temp.iloc[0][[metric]])
    except: m = 'error'
    return m

# cycle to populate metrics for P, S and E in the columns P_metric, S_metric and E_metric in the model_choice df
for i in range(0, model_choice.shape[0]):
    try:
        model_choice['P_metric'][i] = get_metric(i, '1_pred_Prophet/', '__4_model2_metrics.csv', 'MAE')
        model_choice['S_metric'][i] = get_metric(i, '2_pred_Sarima/', '__2_model1_metrics.csv', 'MAE')
        model_choice['E_metric'][i] = get_metric(i, '3_pred_ES/', '__2_model1_metrics.csv', 'MAE')
    except: 
        model_choice['P_metric'][i] = 'N'


# function to choose the best model out of P, S and E
def choose_best_metric(p,s,e):
    if p == 'error':
        p = 10^10
    if s == 'error':
        s = 10^10    
    if e == 'error':
        e = 10^10        

    min_temp = min(p,s,e)
    if min_temp == e:
        out = 'E'
    if min_temp == s:
        out = 'S'    
    if min_temp == p:
        out = 'P'
    if min_temp == 10^10 :
        out = 'N'
    
    return out

# populate the column Best_model_metric  to choose the best model based on MAE recorded in P_metric, S_metric, E_metric columns
model_choice['Best_model_metric'] = list(map(choose_best_metric, model_choice['P_metric'],model_choice['S_metric'],model_choice['E_metric'] ))

# set up column name to use for forecasting in the plot_forecast function
model_choice_col = 'Best_model_metric' # 


####################################################################

# set up a list of file extensions to load model forecasts for Prophet, Sarima and exponential smoothing respectively
file_ext_list = ['___7_model2_forecast.csv', '___4_model1_forecast.csv', '___4_model1_forecast.csv'] 

# set up folder name to save all the outcomes produced by the plot_forecast function
save_folder_sum = '8_temp/'

# create that folder
if not os.path.exists(path+save_folder_sum):
    # If it doesn't exist, create it
    os.makedirs(path+save_folder_sum)


# dictionary to convert one letter names to full names of procedure type to print them on the graphs
proc_dict = {'c':'Colonoscopy','g':'Gastroscopy','s':'Flexible sigmoidoscopy',
             's_c':'Lower GI endoscopy','s_c_all':'Lower GI endoscopy',
             'cgs':'Colonoscopy, flexible sigmoidoscopy and gastroscopy',
             'ecrp':'ERCP', 'All': 'Any endoscopy'}

# get the keys from the dictionary of dictionaries - to iterate over those dictionaries
trusts_keys = list(trusts.keys())




#########################################################################
# master function to plot forecasts for procedures in several sites together or all trusts
def plot_forecast(param_files_list, index_of_interest, file_ext_list, save_folder_sum, save_file_name, model_choice, model_choice_col, trust_name, procedure_type, points_flag):
    # create file with forecasts
    f = []
    for i1 in range(2023,2028):
        for i2 in ['-01-01','-02-01','-03-01','-04-01','-05-01','-06-01','-07-01','-08-01','-09-01','-10-01','-11-01','-12-01']:
            f.append(str(i1)+i2)

    f1 = []
    for i1 in range(2020,2023):
        for i2 in ['-01-01','-02-01','-03-01','-04-01','-05-01','-06-01','-07-01','-08-01','-09-01','-10-01','-11-01','-12-01']:
            f1.append(str(i1)+i2)


    # determine day of the week for the start day defined in - model_choice
    dw1 = datetime.strptime(model_choice['start_w'][0], '%Y-%m-%d').weekday()
    start_date_unif = datetime.strptime(model_choice['start_w'][0], '%Y-%m-%d') - timedelta(days=dw1-1)
    # determine day of the week for the last day defined in - model_choice
    dw2 = datetime.strptime(model_choice['end_w'][0], '%Y-%m-%d').weekday()
    ned_date_unif = datetime.strptime(model_choice['end_w'][0], '%Y-%m-%d') - timedelta(days=dw2-1)    
    
    # list with dates from start to end
    f2 = []
    d = start_date_unif
    while d <= ned_date_unif:
        f2.append( d )
        d = d + timedelta(days=7)  

    # get full procedure name
    proc_name = proc_dict[procedure_type]
    
 
            

    # function to cut Date to format: YYYY-mm-dd
    def cut_str10(a):
        return a[:10]

    def cut_str9(a):
        return a[:9]    

    # function to get half of confidence interval
    def ret_radius_CI(a,b):
        return (a-b)/2
    
    # function to get the date of the closest monday
    def move_to_closest_monday(d):
        return d - timedelta(days=d.weekday()-1)    
                
   
    # create empty output dfs
    f_observed = pd.DataFrame({'ds': f1})
    
    f_obs_test_y = pd.DataFrame({'ds': f2})
    f_obs_test_yhat = pd.DataFrame({'ds': f2})
   
    forecast_1 = pd.DataFrame({'ds': f})   
    forecast_L = pd.DataFrame({'ds': f})   
    forecast_U = pd.DataFrame({'ds': f})  
    # df for radius of CI
    forecast_rad = pd.DataFrame({'ds': f})
    # df with sums and CIs 
    forecast_f = pd.DataFrame({'ds': f}) 
    
    # iterate over the list of indexes of sites (index_of_interest)
    for c in index_of_interest:        
        c = int(c)
        # get best model from the model_choice df        
        best_model = model_choice.iloc[c][[model_choice_col]].to_string(index = False)

        if best_model=='N':
            continue

        # populate outcome tables if the best model is Prophet
        if best_model=='P':            
            # index to get the right file extension for the model from param_files_list
            p=0
            # load the parameters 
            param_temp = pd.read_excel(path0+param_files_list[p], sheet_name = 'params')
            # get the saving path + name
            save_folder_temp = param_temp.iloc[c][['save_folder']].to_string(index = False)
            try:
                # load the data
                file_temp = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                #convert column to str
                file_temp['ds'] = file_temp['ds'].astype(str)
                # cut str to format: YYYY-mm-dd
                file_temp['ds'] = file_temp['ds'].map(cut_str10)
                # add yhat from each site data file to the output forecast_1
                forecast_1 = pd.merge(forecast_1, file_temp[['ds','yhat']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_1 = forecast_1.rename(columns={'yhat':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat'})
                
                # add yhat lower CI limit from each site data file to the output forecast_L                
                forecast_L = pd.merge(forecast_L, file_temp[['ds','yhat_lower']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_L = forecast_L.rename(columns={'yhat_lower':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_lower'})

                # add yhat upper CI limit from each site data file to the output forecast_U               
                forecast_U = pd.merge(forecast_U, file_temp[['ds','yhat_upper']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_U = forecast_U.rename(columns={'yhat_upper':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_upper'})
                
                # get the half of the CI
                file_temp['rad'] = list(map(ret_radius_CI, file_temp['yhat_upper'], file_temp['yhat_lower']))
                forecast_rad = pd.merge(forecast_rad, file_temp[['ds','rad']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_rad = forecast_rad.rename(columns={'rad':  str(c)+'_'+param_files_list[p][7:-4]+'_rad'}) 
                
                # cut the last date digit for subsequent merging of dataframes
                file_temp['ds'] = file_temp['ds'].map(cut_str9)
                f_observed['ds'] = f_observed['ds'].map(cut_str9)
                
                # add y from each site data file to the output f_observed             
                f_observed = pd.merge(f_observed, file_temp[['ds','y']], how="left", on=["ds"])
                f_observed = f_observed.drop_duplicates(subset=['ds'], keep='first')
                # rename the yhat column approprietly 
                f_observed = f_observed.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                f_observed['ds'] = f_observed['ds']+'1'
                


                # create dfs to compare MAE later
                # load the data
                file_temp2 = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                
                # drop rows where y is missing
                file_temp2.dropna(subset=['y'], inplace=True)
                # convert date from string to Timestamp
                file_temp2['ds'] = pd.DatetimeIndex(file_temp2['ds']).normalize()
                # get the date with closest monday   
                file_temp2['ds'] = file_temp2['ds'].map(move_to_closest_monday) 
                # merge dfs to get y based on obtained Monday dates
                f_obs_test_y = pd.merge(f_obs_test_y, file_temp2[['ds','y']], how="left", on=["ds"])
                f_obs_test_y = f_obs_test_y.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                # merge dfs to get yhat based on obtained Monday dates
                f_obs_test_yhat = pd.merge(f_obs_test_yhat, file_temp2[['ds','yhat']], how="left", on=["ds"])
                f_obs_test_yhat = f_obs_test_yhat.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                  
            except: print(c)


        # populate outcome tables if the best model is Sarima
        if best_model=='S':
        #if (param_files_list[p].find('Sarima') !=-1 ):  
            # index to get the right file extension for the model from param_files_list
            p=1
            # load the parameters 
            param_temp = pd.read_excel(path0+param_files_list[p], sheet_name = 'params')

            # get the saving path + name
            save_folder_temp = param_temp.iloc[c][['save_folder']].to_string(index = False)
            try:
                # load the data                
                file_temp = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                file_temp = file_temp.rename(columns={'Unnamed: 0': 'ds'}) 
                
                #convert column to str
                file_temp['ds'] = file_temp['ds'].astype(str)
                # cut str to format: YYYY-mm-dd
                file_temp['ds'] = file_temp['ds'].map(cut_str9)
                forecast_1['ds'] = forecast_1['ds'].map(cut_str9)
                # add yhat from each site data file to the output forecast_1                
                forecast_1 = pd.merge(forecast_1, file_temp[['ds','yhat']], how="left", on=["ds"])
                forecast_1 = forecast_1.drop_duplicates(subset=['ds'], keep='first')
                # rename the yhat column approprietly 
                forecast_1 = forecast_1.rename(columns={'yhat':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat'})
                # add yhat lower CI limit from each site data file to the output forecast_L                    
                forecast_L['ds'] = forecast_L['ds'].map(cut_str9)
                forecast_L = pd.merge(forecast_L, file_temp[['ds','lower y']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_L = forecast_L.drop_duplicates(subset=['ds'], keep='first')
                forecast_L = forecast_L.rename(columns={'lower y':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_lower'})
                
                # add yhat upper CI limit from each site data file to the output forecast_U               
                forecast_U['ds'] = forecast_U['ds'].map(cut_str9)                    
                forecast_U = pd.merge(forecast_U, file_temp[['ds','upper y']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_U = forecast_U.drop_duplicates(subset=['ds'], keep='first')
                forecast_U = forecast_U.rename(columns={'upper y':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_upper'})
                
                # get the half of the CI                
                file_temp['rad'] = list(map(ret_radius_CI, file_temp['upper y'], file_temp['lower y']))
                forecast_rad['ds'] = forecast_rad['ds'].map(cut_str9)                    
                forecast_rad = pd.merge(forecast_rad, file_temp[['ds','rad']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_rad = forecast_rad.drop_duplicates(subset=['ds'], keep='first')
                forecast_rad = forecast_rad.rename(columns={'rad':  str(c)+'_'+param_files_list[p][7:-4]+'_rad'})

                # cut the last date digit for subsequent merging of dataframes
                f_observed['ds'] = f_observed['ds'].map(cut_str9)
                # add y from each site data file to the output f_observed             
                f_observed = pd.merge(f_observed, file_temp[['ds','y']], how="left", on=["ds"])
                f_observed = f_observed.drop_duplicates(subset=['ds'], keep='first')
                # rename the yhat column approprietly 
                f_observed = f_observed.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                f_observed['ds'] = f_observed['ds']+'1'

                
                forecast_1['ds'] = forecast_1['ds']+'1'
                forecast_L['ds'] = forecast_L['ds']+'1'
                forecast_U['ds'] = forecast_U['ds']+'1'
                forecast_rad['ds'] = forecast_rad['ds']+'1'



                # create dfs to compare calculate MAE for sum of sites for the test period (to compare later with the model for sum of observed)
                # load the data
                file_temp2 = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                file_temp2 = file_temp2.rename(columns={'Unnamed: 0': 'ds'}) 
                # drop rows where y is missing                
                file_temp2.dropna(subset=['y'], inplace=True)
                # convert date from string to Timestamp
                file_temp2['ds'] = pd.DatetimeIndex(file_temp2['ds']).normalize()
                # get the date with closest monday   
                file_temp2['ds'] = file_temp2['ds'].map(move_to_closest_monday) 
                # merge dfs to get y based on obtained Monday dates
                f_obs_test_y = pd.merge(f_obs_test_y, file_temp2[['ds','y']], how="left", on=["ds"])
                f_obs_test_y = f_obs_test_y.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                # merge dfs to get yhat based on obtained Monday dates
                f_obs_test_yhat = pd.merge(f_obs_test_yhat, file_temp2[['ds','yhat']], how="left", on=["ds"])
                f_obs_test_yhat = f_obs_test_yhat.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                
            except: print(c)



        # populate outcome tables if the best model is Exponential smoothing (ES)
        if best_model=='E':
        #if (param_files_list[p].find('Sarima') !=-1 ):
            
            # index to get the right file extension for the model from param_files_list
            p=2
            # load the parameters 
            param_temp = pd.read_excel(path0+param_files_list[p], sheet_name = 'params')
            # get the saving path + name
            save_folder_temp = param_temp.iloc[c][['save_folder']].to_string(index = False)
            try:
                # load the data                
                file_temp = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                file_temp = file_temp.rename(columns={'Unnamed: 0': 'ds'}) 
                #convert column to str
                file_temp['ds'] = file_temp['ds'].astype(str)
                # cut str to format: YYYY-mm-dd
                file_temp['ds'] = file_temp['ds'].map(cut_str9)
                
                forecast_1['ds'] = forecast_1['ds'].map(cut_str9)
                # add yhat from each site data file to the output forecast_1
                forecast_1 = pd.merge(forecast_1, file_temp[['ds','yhat']], how="left", on=["ds"])
                forecast_1 = forecast_1.drop_duplicates(subset=['ds'], keep='first')
                # rename the yhat column approprietly 
                forecast_1 = forecast_1.rename(columns={'yhat':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat'})
                # add yhat lower CI limit from each site data file to the output forecast_L                    
                forecast_L['ds'] = forecast_L['ds'].map(cut_str9)
                forecast_L = pd.merge(forecast_L, file_temp[['ds','pi_lower']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_L = forecast_L.drop_duplicates(subset=['ds'], keep='first')
                forecast_L = forecast_L.rename(columns={'pi_lower':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_lower'})
                
                # add yhat upper CI limit from each site data file to the output forecast_U               
                forecast_U['ds'] = forecast_U['ds'].map(cut_str9)                    
                forecast_U = pd.merge(forecast_U, file_temp[['ds','pi_upper']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_U = forecast_U.drop_duplicates(subset=['ds'], keep='first')
                forecast_U = forecast_U.rename(columns={'pi_upper':  str(c)+'_'+param_files_list[p][7:-4]+'_yhat_upper'})
                
                # get the half of the CI
                file_temp['rad'] = list(map(ret_radius_CI, file_temp['pi_upper'], file_temp['pi_lower']))
                forecast_rad['ds'] = forecast_rad['ds'].map(cut_str9)                    
                forecast_rad = pd.merge(forecast_rad, file_temp[['ds','rad']], how="left", on=["ds"])
                # rename the yhat column approprietly 
                forecast_rad = forecast_rad.drop_duplicates(subset=['ds'], keep='first')
                forecast_rad = forecast_rad.rename(columns={'rad':  str(c)+'_'+param_files_list[p][7:-4]+'_rad'})

                # cut the last date digit for subsequent merging of dataframes
                f_observed['ds'] = f_observed['ds'].map(cut_str9)
                # add y from each site data file to the output f_observed             
                f_observed = pd.merge(f_observed, file_temp[['ds','y']], how="left", on=["ds"])
                f_observed = f_observed.drop_duplicates(subset=['ds'], keep='first')
                # rename the yhat column approprietly 
                f_observed = f_observed.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                f_observed['ds'] = f_observed['ds']+'1'
                forecast_1['ds'] = forecast_1['ds']+'1'
                forecast_L['ds'] = forecast_L['ds']+'1'
                forecast_U['ds'] = forecast_U['ds']+'1'
                forecast_rad['ds'] = forecast_rad['ds']+'1'
                
                
                # create dfs to compare MAE later
                # load the data                
                file_temp2 = pd.read_csv(  path0+save_folder_temp+ file_ext_list[p] )
                file_temp2 = file_temp2.rename(columns={'Unnamed: 0': 'ds'}) 
                # drop rows where y is missing                
                file_temp2.dropna(subset=['y'], inplace=True)
                # convert date from string to Timestamp
                file_temp2['ds'] = pd.DatetimeIndex(file_temp2['ds']).normalize()
                # get the date with closest monday               
                file_temp2['ds'] = file_temp2['ds'].map(move_to_closest_monday) 
                # merge dfs to get y based on obtained Monday dates
                f_obs_test_y = pd.merge(f_obs_test_y, file_temp2[['ds','y']], how="left", on=["ds"])
                f_obs_test_y = f_obs_test_y.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                # merge dfs to get yhat based on obtained Monday dates                
                f_obs_test_yhat = pd.merge(f_obs_test_yhat, file_temp2[['ds','yhat']], how="left", on=["ds"])
                f_obs_test_yhat = f_obs_test_yhat.rename(columns={'y':  str(c)+'_'+param_files_list[p][7:-4]+'_y'})
                
                
            except: print(c)
    
    # copy dfs for later analysis of points
    if points_flag==1:
        f_observed_p = copy.deepcopy(f_observed)
        forecast_1_p = copy.deepcopy(forecast_1)
        forecast_L_p = copy.deepcopy(forecast_L)
        forecast_U_p = copy.deepcopy(forecast_U)
        forecast_rad_p = copy.deepcopy(forecast_rad)
        forecast_f_p = pd.DataFrame({'ds': f}) 
        
        
    # drop missing data in observed df
    f_observed = f_observed.dropna()
    # add column for sums
    f_observed['sum_o'] = f_observed.sum(axis=1)
    
    # make predictions non negatice for future summing       
    forecast_1 = forecast_1.applymap(lambda x: 0 if isinstance(x, (int, float)) and x < 0 else x)
    # make predictions integers              
    forecast_1 = forecast_1.applymap(lambda x: int(x) if ( isinstance(x, (int, float)) and not math.isnan( x ) ) else x)

    # get sums of various sites
    forecast_1['sum'] = forecast_1.sum(axis=1)
    forecast_L['CI_Lower_additive'] = forecast_L.sum(axis=1)
    forecast_U['CI_Upper_additive'] = forecast_U.sum(axis=1)
    
    # get sum of squarees of radiuses
    forecast_rad2=forecast_rad.iloc[:,1:forecast_rad.shape[1]].apply(lambda num: num**2) #Square of each number stored in new.
    forecast_rad2['sum_sq_rad'] = forecast_rad2.sum(axis=1)
    forecast_rad2['sqrt_sum_sq_rad'] = list(map(lambda n: math.sqrt(n), forecast_rad2['sum_sq_rad']))
    forecast_rad2['ds'] = forecast_rad['ds']
    
    
        
    # create final table with all forecast info including CI (conservative and for independent variables assumption)
    forecast_f = pd.merge(forecast_f, forecast_1[['ds','sum']], how="left", on=["ds"])
    forecast_f = pd.merge(forecast_f, forecast_L[['ds','CI_Lower_additive']], how="left", on=["ds"])
    forecast_f = pd.merge(forecast_f, forecast_U[['ds','CI_Upper_additive']], how="left", on=["ds"])
    forecast_f = pd.merge(forecast_f, forecast_rad2[['ds','sqrt_sum_sq_rad']], how="left", on=["ds"])
    forecast_f['CI_Lower_indep'] = forecast_f['sum'] -  forecast_f['sqrt_sum_sq_rad']  
    forecast_f['CI_Upper_indep'] = forecast_f['sum'] + forecast_f['sqrt_sum_sq_rad']  
    
    
    
    ### get metrics to assess performance of best models on the set of sites during the test period
    # get sums of y   
    f_obs_test_y = f_obs_test_y[f_obs_test_y['ds']<= '2022-12-27']
    f_obs_test_y.fillna(method='ffill', inplace=True)
    f_obs_test_y.set_index(f_obs_test_y.columns[0], inplace=True)
    f_obs_test_y = f_obs_test_y.dropna()
    f_obs_test_y['sum_y'] = f_obs_test_y.sum(axis=1)
    f_obs_test_y.reset_index(inplace=True)
    # get sums of yhat
    f_obs_test_yhat = f_obs_test_yhat[f_obs_test_yhat['ds']<= '2022-12-27']
    f_obs_test_yhat.fillna(method='ffill', inplace=True)
    f_obs_test_yhat.set_index(f_obs_test_yhat.columns[0], inplace=True)
    f_obs_test_yhat = f_obs_test_yhat.dropna()
    f_obs_test_yhat['sum_yhat'] = f_obs_test_yhat.sum(axis=1)
    f_obs_test_yhat.reset_index(inplace=True)
    
    # merge dfs with y and yhat
    f_obs_test = f_obs_test_y[['ds','sum_y']]
    f_obs_test = pd.merge(f_obs_test, f_obs_test_yhat[['ds','sum_yhat']], how="left", on=["ds"])
    f_obs_test = f_obs_test.dropna()
    f_obs_test.to_csv(path + save_folder_sum + save_file_name + '8_test_y_that.csv')

    # save the file with metrics
    f_obs_test_metrics = pd.read_csv(path + save_folder_sum + '___'+'__summed_test_metrics.csv')
    f_obs_test_metrics_temp = pd.DataFrame({
       "Condition": [save_file_name],
       "MSE": [round(  mean_squared_error(f_obs_test['sum_yhat'], f_obs_test['sum_y']), 0)],
       "RMSE": [round(  mean_squared_error(f_obs_test['sum_yhat'], f_obs_test['sum_y'], squared = False), 0)],
       "MAPE": [round(  mean_absolute_percentage_error(f_obs_test['sum_yhat'], f_obs_test['sum_y']), 2)],
       "MAE": [round(  mean_absolute_error(f_obs_test['sum_yhat'], f_obs_test['sum_y']), 0)] })
    
    f_obs_test_metrics = pd.concat([f_obs_test_metrics, f_obs_test_metrics_temp], axis = 0)
    f_obs_test_metrics.to_csv(path + save_folder_sum + '___'+'__summed_test_metrics.csv', index = False)
    #########################################################


    # merge df with observed and forecasted data
    fin = pd.merge(f_observed[['ds','sum_o']], forecast_f, how="outer", on=["ds"])
    fin['ds2'] = 0
    for i in range(0,fin.shape[0]):
        fin['ds2'][i] = datetime.strptime( fin['ds'][i], '%Y-%m-%d')
    fin = fin.sort_values('ds2')
    


    ####################
    # PLOT 1 Endoscopies: prediction + CI 
        # regression to get what is yearly change compared to the average prediction for the 2023  
    regression2 = LinearRegression()
    regression2.fit( np.arange(1, 61).reshape(-1, 1) , fin[fin['ds']>='2023-01']['sum'].values.reshape(-1, 1))
    coefficients = regression2.coef_
    intercept = regression2.intercept_
    coefficients12 = coefficients*12
    
    result = list(map(lambda x: coefficients.item()*x + intercept.item(), np.arange(1, 61)))
    
    plt.plot(np.arange(1, 61).reshape(-1, 1), fin[fin['ds']>='2023-01']['sum'].values.reshape(-1, 1), color='blue', label='Original Data')
    plt.plot(np.arange(1, 61).reshape(-1, 1), result, color='red', label='Fitted Line')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Linear Regression')
    plt.legend()
    plt.savefig( path + save_folder_sum + save_file_name + '9_yearly_change_compared_to_av2023.jpg', dpi=300, transparent  = True, format='jpg')
    plt.show()
    plt.close()
        #change compared to the average prediction for the 2023  
    change_yearly = np.round( coefficients12 / fin[ (fin['ds']>='2023-01') & (fin['ds']<='2023-12') ]['sum'].mean() *100, 1 )
    #if fin[fin.CI_Lower_indep < 0].shape[0] > 0:
    
    # Plot the main plot
        # Get mean observation for year 2022         
    mean2022_obs = fin[ (fin['ds']>='2022-01') & (fin['ds']<='2022-12') ]['sum_o'].mean()
        # make a column with regression line
    ind2023_01 = fin.index[fin['ds'] == '2023-01-01'].item()
    # add column with the regression line
    fin['regr'] = [np.nan]*(ind2023_01) + result
    
    # parameter to adjust y location of text labels on the graphs
    magn = 1.25
    if save_file_name.find('LNW') != -1:     # set magn slightly different for LNW trust
        magn = 1.35           
    
    if save_file_name.find('HealthShare') != -1:      # set magn slightly different for HealthShare trust
       magn = 1.65
        
        
    # plot the main graph with observed, predicted lines, CIs, and the line regressed to the forecast as well as text showing the changes
    ax = fin.plot(x = 'ds', y = 'sum',label='predicted',linewidth=3,alpha=1, figsize=(14, 14))   # , color = 'orange'
    ax.xaxis_date()
    fin.plot(x = 'ds', y = 'sum_o', ax=ax, label='observed', alpha=.7, linewidth=3, color='black')
    fin.plot(x = 'ds', y = 'regr', ax=ax, label='line fitted to the prediction', alpha=.7, linewidth=1, color='blue')
    ax.fill_between(fin.index,fin['CI_Lower_additive'],fin['CI_Upper_additive'],color='k', alpha=.2)
    ax.fill_between(fin.index,fin['CI_Lower_indep'],fin['CI_Upper_indep'], color='r', alpha=.2)
    
    plt.legend(fontsize=18, loc="upper right")
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=14)
    plt.xlabel("Date", fontsize=18)
    plt.ylabel("Estimated visits per week", fontsize=18)
    
    # set up ticks - only first month of each year
            # Get indexes where the substring contains the pattern:     
    ind_list = fin[fin['ds'].str.contains('-01-')].index.tolist()
            # Get values from the column based on the indexes:       df['Column'].iloc[indexes].tolist()
    ind_list_val = fin['ds'].iloc[ind_list].tolist()
    plt.xticks(ind_list, ind_list_val, rotation=45, ha='right')
    plt.title(trust_name+': '+proc_name, fontsize=24)
    # limit y axis with 0 and plot line that crosses 0 when non conservative lower CI reach 0
    plt.ylim(bottom=0)
    if fin[fin.CI_Lower_indep < 0].shape[0] > 0:
        ax.axvline(x=fin[fin.CI_Lower_indep < 0].iloc[0].name, color='r', linestyle='--')
        plt.text(fin[fin.CI_Lower_indep < 0].iloc[0].name, 0,'  CI goes below 0: '+fin[fin.CI_Lower_indep < 0].iloc[0].ds, 
                 fontsize=14, color = 'red', rotation=0)
           
    # add texts with numbers reflecting changes in prediction compared to average 2022 value
    mean2023_pred =  fin[ (fin['ds']>='2023-01') & (fin['ds']<='2023-12') ]['sum'].mean()
    plt.text(fin[fin['ds2'] == datetime(2023, 1, 1, 0, 0)].iloc[0].name, fin[fin['ds2'] == datetime(2023, 1, 1, 0, 0)]['sum']*0.65,
             'Mean 2023 / \nMean 2022:  \n'+str( round( mean2023_pred/mean2022_obs, 2) ), fontsize=13, color = 'darkblue', rotation=0)
    plt.text(fin[fin['ds2'] == datetime(2025, 1, 1, 0, 0)].iloc[0].name, fin[fin['ds2'] == datetime(2025, 1, 1, 0, 0)]['sum']*0.65,
             'Mean 2025 / \nMean 2022:  \n'+str( round( fin[ (fin['ds']>='2025-01') & (fin['ds']<='2025-12') ]['sum'].mean() /mean2022_obs, 2) ), fontsize=13, color = 'darkblue', rotation=0)
    plt.text(fin[fin['ds2'] == datetime(2027, 1, 1, 0, 0)].iloc[0].name, fin[fin['ds2'] == datetime(2027, 1, 1, 0, 0)]['sum']*0.65,
             'Mean 2027 / \nMean 2022:  \n'+str( round( fin[ (fin['ds']>='2027-01') & (fin['ds']<='2027-12') ]['sum'].mean() /mean2022_obs, 2) ), fontsize=13, color = 'darkblue', rotation=0)
    # Plot yearly change estimated from regression line
    plt.text(fin[fin['ds2'] == datetime(2025, 1, 1, 0, 0)].iloc[0].name, fin[fin['ds']>='2023-01']['sum'].max()*magn,
             'Yearly change estimated from \nregression line (% of av. 2023 visits):  \n'+str( int( np.round( coefficients12.item(), 0 ) ) ) +'  ('+ str(np.round(coefficients12.item()/mean2023_pred*100,2))+'%)',
             fontsize=13, color = 'blue', rotation=0)
    # Average 2022 visits
    plt.text(fin[fin['ds2'] == datetime(2022, 1, 1, 0, 0)].iloc[0].name, fin[((fin['ds']>='2022-01') & (fin['ds']<='2022-12'))]['sum_o'].max(),
             'Average 2022 \nvisits: '+str( int( round( mean2022_obs, 0) ) ), fontsize=13, color = 'blue', rotation=0)
    # Average 2023 visits:
    plt.text(fin[fin['ds2'] == datetime(2023, 2, 1, 0, 0)].iloc[0].name, fin[((fin['ds']>='2023-01') & (fin['ds']<='2023-12'))]['sum'].max()*magn,
             'Average 2023 \nvisits: '+str( int( round( fin[ (fin['ds']>='2023-01') & (fin['ds']<='2023-12') ]['sum'].mean(), 1) ) ), fontsize=13, color = 'blue', rotation=0)
     
    plt.savefig( path + save_folder_sum + save_file_name + '1_CI.jpg', dpi=300, transparent  = True, format='jpg')
    plt.show()
    plt.close()
    
    
    ####################
    # PLOT 2 Endoscopies: same as Plot 1 but forecast without CI        
    ax = fin.plot(x = 'ds', y = 'sum',label='predicted',linewidth=3,alpha=1, figsize=(14, 14))   # , color = 'orange'
    ax.xaxis_date()
    fin.plot(x = 'ds', y = 'sum_o', ax=ax, label='observed', alpha=.7, linewidth=3, color='black')
    plt.legend(fontsize=18, loc="upper right")
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=14)
    plt.xlabel("Date", fontsize=18)
    plt.ylabel("Estimated visits per week", fontsize=18)
    plt.xticks(ind_list, ind_list_val, rotation=45, ha='right')
    plt.title(trust_name+': '+proc_name, fontsize=24)
    plt.ylim(bottom=0)

    plt.savefig( path + save_folder_sum + save_file_name + '2_noCI.jpg', dpi=300, transparent  = True, format='jpg')
    plt.show()
    plt.close()       

    # save the tables
    f_observed.to_csv(path + save_folder_sum + save_file_name + '0_observed.csv')
    forecast_1.to_csv(path + save_folder_sum + save_file_name + '1_forecast_raw.csv')
    forecast_L.to_csv(path + save_folder_sum + save_file_name + '2_forecast_L.csv')
    forecast_U.to_csv(path + save_folder_sum + save_file_name + '3_forecast_U.csv')
    forecast_rad.to_csv(path + save_folder_sum + save_file_name + '4_forecast_rad.csv')
    forecast_f.to_csv(path + save_folder_sum + save_file_name + '5_forecast_final.csv')


    ################################################################################
    # make plots for total points (not the number of endoscopies)
    if points_flag==1:


        # iterate over the list of indexes of sites (index_of_interest)
        for c in index_of_interest:
            try:
                # average points for the current c (current site and procedure)
                m = model_choice.iloc[c][['Av_points']][0]
                
                # Observed: get column name for the current c for a df
                    # convert endoscopy visit into points using m
                col_name1 = f_observed_p.columns[f_observed_p.columns.str.startswith(str(c)+'_')][0]
                f_observed_p[col_name1] = f_observed_p[col_name1].apply(lambda x: x*m)

                # Forecast: get column name for the current c for a df
                    # convert endoscopy visit into points using m                
                col_name2 = forecast_1_p.columns[forecast_1_p.columns.str.startswith(str(c)+'_')][0]
                forecast_1_p[col_name2] = forecast_1_p[col_name2].apply(lambda x: x*m)

                # Lower CI: get column name for the current c for a df
                    # convert endoscopy visit into points using m
                col_name3 = forecast_L_p.columns[forecast_L_p.columns.str.startswith(str(c)+'_')][0]
                forecast_L_p[col_name3] = forecast_L_p[col_name3].apply(lambda x: x*m)

                # Upper CI: get column name for the current c for a df
                    # convert endoscopy visit into points using m
                col_name4 = forecast_U_p.columns[forecast_U_p.columns.str.startswith(str(c)+'_')][0]
                forecast_U_p[col_name4] = forecast_U_p[col_name4].apply(lambda x: x*m)
 
                # Half CI: get column name for the current c for a df
                    # convert endoscopy visit into points using m
                col_name5 = forecast_rad_p.columns[forecast_rad_p.columns.str.startswith(str(c)+'_')][0]
                forecast_rad_p[col_name5] = forecast_rad_p[col_name5].apply(lambda x: x*m)
            except: 'error'
    
        # Observed: remove missing values
        f_observed_p = f_observed_p.dropna()
        # Get sum for each date (row)
        f_observed_p['sum_o'] = f_observed_p.sum(axis=1)
        
        # make predictions non negative for future summing       
        forecast_1_p = forecast_1_p.applymap(lambda x: 0 if isinstance(x, (int, float)) and x < 0 else x)
        # make predictions integers              
        forecast_1_p = forecast_1_p.applymap(lambda x: int(x) if ( isinstance(x, (int, float)) and not math.isnan( x ) ) else x)

        # get row sums for Forecasts, Lower CI and upper CI
        forecast_1_p['sum'] = forecast_1_p.sum(axis=1)
        forecast_L_p['CI_Lower_additive'] = forecast_L_p.sum(axis=1)
        forecast_U_p['CI_Upper_additive'] = forecast_U_p.sum(axis=1)
        
        # get sum of squarees of radiuses
        forecast_rad2_p = forecast_rad_p.iloc[:,1:forecast_rad_p.shape[1]].apply(lambda num: num**2) #Square of each number stored in new.
        forecast_rad2_p['sum_sq_rad'] = forecast_rad2_p.sum(axis=1)
        forecast_rad2_p['sqrt_sum_sq_rad'] = list(map(lambda n: math.sqrt(n), forecast_rad2_p['sum_sq_rad']))
        forecast_rad2_p['ds'] = forecast_rad_p['ds']
        
        
            
        # create final table with all forecast info including CI (conservative and for independent variables assumption)
        forecast_f_p = pd.merge(forecast_f_p, forecast_1_p[['ds','sum']], how="left", on=["ds"])
        forecast_f_p = pd.merge(forecast_f_p, forecast_L_p[['ds','CI_Lower_additive']], how="left", on=["ds"])
        forecast_f_p = pd.merge(forecast_f_p, forecast_U_p[['ds','CI_Upper_additive']], how="left", on=["ds"])
        forecast_f_p = pd.merge(forecast_f_p, forecast_rad2_p[['ds','sqrt_sum_sq_rad']], how="left", on=["ds"])
        forecast_f_p['CI_Lower_indep'] = forecast_f_p['sum'] -  forecast_f_p['sqrt_sum_sq_rad']  
        forecast_f_p['CI_Upper_indep'] = forecast_f_p['sum'] + forecast_f_p['sqrt_sum_sq_rad'] 
 


        # create final table with observed data and the forecast
        fin_p = pd.merge(f_observed_p[['ds','sum_o']], forecast_f_p, how="outer", on=["ds"])
        fin_p['ds2'] = 0
        for i in range(0,fin_p.shape[0]):
            fin_p['ds2'][i] = datetime.strptime( fin_p['ds'][i], '%Y-%m-%d')
        fin_p = fin_p.sort_values('ds2')
        
       
        ####################
        # PLOT 1 Points: prediction + CI 
        # regression to get what is yearly change compared to the average prediction for the 2023  
        regression3 = LinearRegression()
        regression3.fit( np.arange(1, 61).reshape(-1, 1) , fin_p[fin_p['ds']>='2023-01']['sum'].values.reshape(-1, 1))
        coefficients_p = regression3.coef_
        intercept_p = regression3.intercept_
        coefficients12_p = coefficients_p*12
        
        result_p = list(map(lambda x: coefficients_p.item()*x + intercept_p.item(), np.arange(1, 61)))
        
        plt.plot(np.arange(1, 61).reshape(-1, 1), fin_p[fin_p['ds']>='2023-01']['sum'].values.reshape(-1, 1), color='blue', label='Original Data')
        plt.plot(np.arange(1, 61).reshape(-1, 1), result_p, color='red', label='Fitted Line')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Linear Regression')
        plt.legend()
        plt.savefig( path + save_folder_sum + save_file_name + '_p_9_yearly_change_compared_to_av2023.jpg', dpi=300, transparent  = True, format='jpg')
        plt.show()
        plt.close()
            #change compared to the average prediction for the 2023  
        change_yearly_p = np.round( coefficients12_p / fin_p[ (fin_p['ds']>='2023-01') & (fin_p['ds']<='2023-12') ]['sum'].mean() *100, 1 )
  
            #if fin[fin.CI_Lower_indep < 0].shape[0] > 0:
        #    fin2 = fin.iloc[0:fin[fin.CI_Lower_indep < 0].iloc[0].name, :]
            # Get mean observation for year 2022         
        mean2022_obs_p = fin_p[ (fin_p['ds']>='2022-01') & (fin_p['ds']<='2022-12') ]['sum_o'].mean()
            # make a column with regression line
        ind2023_01_p = fin_p.index[fin['ds'] == '2023-01-01'].item()
        fin_p['regr'] = [np.nan]*(ind2023_01_p) + result_p
                   
        # plot the main graph with observed, predicted lines, CIs, and the line regressed to the forecast as well as text showing the changes
        ax = fin_p.plot(x = 'ds', y = 'sum',label='predicted',linewidth=3,alpha=1, figsize=(14, 14))   # , color = 'orange'
        ax.xaxis_date()
        fin_p.plot(x = 'ds', y = 'sum_o', ax=ax, label='observed', alpha=.7, linewidth=3, color='black')
        fin_p.plot(x = 'ds', y = 'regr', ax=ax, label='line fitted to the prediction', alpha=.7, linewidth=1, color='blue')
        ax.fill_between(fin_p.index,fin_p['CI_Lower_additive'],fin_p['CI_Upper_additive'],color='k', alpha=.2)
        ax.fill_between(fin_p.index,fin_p['CI_Lower_indep'],fin_p['CI_Upper_indep'], color='r', alpha=.2)
        plt.legend(fontsize=18, loc="upper right")
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.tick_params(axis='both', which='minor', labelsize=14)
        plt.xlabel("Date", fontsize=18)
        plt.ylabel("Estimated points per week", fontsize=18)
        # set up ticks - only first month of each year
                # Get indexes where the substring contains the pattern:     
        ind_list_p = fin_p[fin_p['ds'].str.contains('-01-')].index.tolist()
                # Get values from the column based on the indexes:       df['Column'].iloc[indexes].tolist()
        ind_list_val_p = fin_p['ds'].iloc[ind_list_p].tolist()
        plt.xticks(ind_list_p, ind_list_val_p, rotation=45, ha='right')
        #
        plt.xticks(rotation=45, ha='right')
        plt.title(trust_name+': '+proc_name, fontsize=24)
        # limit y axis with 0 and plot line that crosses 0 when non conservative lower CI reach 0
        plt.ylim(bottom=0)
        if fin_p[fin_p.CI_Lower_indep < 0].shape[0] > 0:
            ax.axvline(x=fin_p[fin_p.CI_Lower_indep < 0].iloc[0].name, color='r', linestyle='--')
            plt.text(fin_p[fin_p.CI_Lower_indep < 0].iloc[0].name, 0,'  CI goes below 0: '+fin_p[fin_p.CI_Lower_indep < 0].iloc[0].ds, 
                     fontsize=14, color = 'red', rotation=0)
        # add texts with numbers reflecting changes in prediction compared to average 2022 value
        mean2023_pred_p =  fin_p[ (fin_p['ds']>='2023-01') & (fin_p['ds']<='2023-12') ]['sum'].mean()
        plt.text(fin_p[fin_p['ds2'] == datetime(2023, 1, 1, 0, 0)].iloc[0].name, fin_p[fin_p['ds2'] == datetime(2023, 1, 1, 0, 0)]['sum']*0.65,
                 'Mean 2023 / \nMean 2022: \n'+str( round( mean2023_pred_p/mean2022_obs_p, 2) ), fontsize=13, color = 'blue', rotation=0)
        plt.text(fin_p[fin_p['ds2'] == datetime(2025, 1, 1, 0, 0)].iloc[0].name, fin_p[fin_p['ds2'] == datetime(2025, 1, 1, 0, 0)]['sum']*0.65,
                 'Mean 2025 / \nMean 2022: \n'+str( round( fin_p[ (fin_p['ds']>='2025-01') & (fin_p['ds']<='2025-12') ]['sum'].mean() /mean2022_obs_p, 2) ), fontsize=13, color = 'blue', rotation=0)
        plt.text(fin_p[fin_p['ds2'] == datetime(2027, 1, 1, 0, 0)].iloc[0].name, fin_p[fin_p['ds2'] == datetime(2027, 1, 1, 0, 0)]['sum']*0.65,
                 'Mean 2027 / \nMean 2022: \n'+str( round( fin_p[ (fin_p['ds']>='2027-01') & (fin_p['ds']<='2027-12') ]['sum'].mean() /mean2022_obs_p, 2) ), fontsize=13, color = 'blue', rotation=0)
        # Plot yearly change estimated from regression line
        plt.text(fin_p[fin_p['ds2'] == datetime(2025, 1, 1, 0, 0)].iloc[0].name, fin_p[fin_p['ds']>='2023-01']['sum'].max()*magn,
             'Yearly change estimated from \nregression line (% of av. 2023 points):  \n'+str( int( np.round( coefficients12_p.item(), 0 ) ) ) +'  ('+ str(np.round(coefficients12_p.item()/mean2023_pred_p*100,2))+'%)',
             fontsize=13, color = 'blue', rotation=0)
        # Average 2022 visits
        plt.text(fin_p[fin_p['ds2'] == datetime(2022, 1, 1, 0, 0)].iloc[0].name, fin_p[((fin_p['ds']>='2022-01') & (fin_p['ds']<='2022-12'))]['sum_o'].max(),
                 'Average 2022 \npoints: '+str( int( round( mean2022_obs_p, 0) ) ), fontsize=13, color = 'blue', rotation=0)
        # Average 2023 visits:
        plt.text(fin_p[fin_p['ds2'] == datetime(2023, 2, 1, 0, 0)].iloc[0].name, fin_p[((fin_p['ds']>='2023-01') & (fin_p['ds']<='2023-12'))]['sum'].max()*magn,
                 'Average 2023 \npoints: '+str( int( round( fin_p[ (fin_p['ds']>='2023-01') & (fin_p['ds']<='2023-12') ]['sum'].mean(), 1) ) ), fontsize=13, color = 'blue', rotation=0)
       
        plt.savefig( path + save_folder_sum + save_file_name + '_p_1_CI.jpg', dpi=300, transparent  = True, format='jpg')
        plt.show()
        plt.close()
        
        # type(fin['ds'][0])

        
        
        ####################
        # PLOT 2 Points: same as Plot 1 but forecast without CI
        ax = fin_p.plot(x = 'ds', y = 'sum',label='predicted',linewidth=3,alpha=1, figsize=(14, 14))   # , color = 'orange'
        ax.xaxis_date()
        fin_p.plot(x = 'ds', y = 'sum_o', ax=ax, label='observed', alpha=.7, linewidth=3, color='black')
        
        plt.legend(fontsize=18, loc="upper right")
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.tick_params(axis='both', which='minor', labelsize=14)
        plt.xlabel("Date", fontsize=18)
        plt.ylabel("Estimated points per week", fontsize=18)
        plt.xticks(ind_list_p, ind_list_val_p, rotation=45, ha='right')
        plt.title(trust_name+': '+proc_name, fontsize=24)
        plt.ylim(bottom=0)

        plt.savefig( path + save_folder_sum + save_file_name + '_p_2_noCI.jpg', dpi=300, transparent  = True, format='jpg')
        plt.show()
        plt.close()       
              
            
        # save the tables
        f_observed_p.to_csv(path + save_folder_sum + save_file_name + '0_observed_p.csv')
        forecast_1_p.to_csv(path + save_folder_sum + save_file_name + '1_forecast_raw_p.csv')
        forecast_L_p.to_csv(path + save_folder_sum + save_file_name + '2_forecast_L_p.csv')
        forecast_U_p.to_csv(path + save_folder_sum + save_file_name + '3_forecast_U_p.csv')
        forecast_rad_p.to_csv(path + save_folder_sum + save_file_name + '4_forecast_rad_p.csv')
        forecast_f_p.to_csv(path + save_folder_sum + save_file_name + '5_forecast_final_p.csv')





# table to save various metrics (MSE, RMSE, MAPE, MAE) for each site (or sum of sites forecasts) for 2022 test period for the best selected model
f_obs_test_metrics = pd.DataFrame({
           "Condition": [], 
           "MSE": [],
           "RMSE": [],
           "MAPE": [],
           "MAE": []})
# save the empty table
f_obs_test_metrics.to_csv(path + save_folder_sum + '___'+'__summed_test_metrics.csv', index = False)


# iterate over trusts and types of procedures using plot_forecast master function
for i in range(0, len(trusts_keys)):
    i=0
    # names for procedures
    proc_keys = list( trusts[trusts_keys[i]].keys() )
    # iterate over types of procedures
    for j in range(0, len(proc_keys)):
        j=0
        print(str(i)+'------------------'+ str(j))
        # get list of indexes of sites/procedures to include in the summing for forecasting
        index_of_interest = trusts[trusts_keys[i]][proc_keys[j]]
        if len(index_of_interest)==0 or index_of_interest == [37]:
            continue
        # get trust name
        trust_name = trusts_keys[i]
        # get procedure name 
        procedure_type = proc_keys[j]
        
        # flag to include graphs for points
        points_flag = 0
        if procedure_type == 'All':
            points_flag = 1
        
        # name for saving    
        save_file_name = str(i)+'_'+trusts_keys[i] +'__'+str(j)+'_'+proc_keys[j]+'__'
        
        # running the main function plot_forecast to get final graphs and analysis with forecasts for sum of sites
        plot_forecast(param_files_list, index_of_interest, file_ext_list, save_folder_sum, save_file_name, model_choice, model_choice_col, trust_name, procedure_type, points_flag)

























































































