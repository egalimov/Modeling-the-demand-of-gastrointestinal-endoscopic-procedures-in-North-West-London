# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 20:29:16 2023

@author: EvgenyGalimov
"""

import pandas as pd
from datetime import datetime
import datetime
import os


# loading and combining the data 
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/'
combined_BCSP = pd.read_csv(path+'Data/'+'4_BCSP_combined.csv')
combined_LNW = pd.read_csv(path+'Data/'+'3_LMW_BCSP.csv')
combined_LNW = combined_LNW.drop(columns = ['Patients number', 'Patient#'])

combined = pd.concat([combined_BCSP, combined_LNW], axis=0, sort=False)


# checking the data
combined_BCSP['Hospital site'].value_counts()
combined_BCSP['Procedure category'].value_counts()
combined_BCSP['Visit type'].value_counts()

combined_LNW['Hospital site'].value_counts()
combined_LNW['Procedure category'].value_counts()
combined_LNW['Visit type'].value_counts()

combined['Hospital site'].value_counts()
combined['Procedure category'].value_counts()
combined['Visit type'].value_counts()


# remove sites (CMH EH) with small counts (1 and 2) from LNW 
combined = combined[combined['Hospital site'] != 'CMH']
combined = combined[combined['Hospital site'] != 'EH']
combined = combined[combined['Procedure category'] != 'CTC']



df = combined


# function to get the time series with weekly counts
def get_table_with_weekly_counts(df, Hospital_site, Procedure_category):
    combined = df

    # select rows related to hospital site and Procedure category of interest
    c = combined[(combined['Hospital site']==Hospital_site)&(combined['Procedure category']==Procedure_category)]

    # format the date
    c[ 'Date' ] = pd.to_datetime(c[ 'Date' ], format = '%Y-%m-%d')
    c[ 'Date' ].value_counts()
    
    # set up list with week dates
    weeks = []
    for i in range(   0, (  (c[c['Visit type']!='Removal' ]['Date'].max() - c['Date'].min())/7   ).days + 1  ):
        weeks.append( c['Date'].min()+datetime.timedelta(days=7*i) )
    
    # define the output df 
    c_time_ser = pd.DataFrame(weeks, columns =['week_first_day'])
    c_time_ser['Referrals'] = 0
    c_time_ser['Rebookings'] = 0
    c_time_ser['Emergency'] = 0
    c_time_ser['Surveilance'] = 0
    c_time_ser['Removals'] = 0
    
    
    # populate the output df with counts aggregated per week for Referrals, Rebookings, Emergency, Surveilance and Removals
    for i in range(0, c_time_ser.shape[0]):
        temp = c[ (c['Date']>=c_time_ser.iloc[i,0] ) & (c['Date']< c_time_ser.iloc[i,0]+datetime.timedelta(days=7) )]
        c_time_ser.loc[c_time_ser.index[i], 'Referrals'] = temp[temp['Visit type'] == 'Referral'].shape[0]
        c_time_ser.loc[c_time_ser.index[i], 'Surveilance'] = temp[temp['Visit type'] == 'Surveillance'].shape[0]
        c_time_ser.loc[c_time_ser.index[i], 'Emergency'] = temp[temp['Visit type'] == 'Emergency'].shape[0]
        c_time_ser.loc[c_time_ser.index[i], 'Rebookings'] = temp[temp['Visit type'] == 'Rebooking'].shape[0]
        c_time_ser.loc[c_time_ser.index[i], 'Removals'] = temp[temp['Visit type'] == 'Removal'].shape[0]
    
    # calculate the weekly visits
    c_time_ser['n_visits'] = c_time_ser['Referrals']+c_time_ser['Rebookings']+c_time_ser['Emergency']+c_time_ser['Surveilance']-c_time_ser['Removals']
    
    return c_time_ser




###### set up lists to iterate over Procedure category and Hospital site
procedures_list = list(combined['Procedure category'].value_counts().index)
hospital_site_list = list(combined['Hospital site'].value_counts().index)


# create a folder
res_folder = '4_BCSP_combined/'
if not os.path.exists(path+'Results/'+res_folder):
   os.makedirs(path+'Results/'+res_folder)




# iterate over Procedure category and Hospital site to create weekly counts
n = 0
for i in hospital_site_list[0:3]:
    for j in procedures_list[0:2]:
        
        print(i, '_', j)

        Hospital_site = i
        Procedure_category = j

        # save original data slice for Hospital site and procedure code
        c = combined[(combined['Hospital site']==Hospital_site)&(combined['Procedure category']==Procedure_category)]
        c = c.sort_values(by=['Date'], ascending = [True])        
        c.to_csv(path+'Results/'+res_folder+str(n)+'_'+Hospital_site+'_'+Procedure_category+'_sliced_data.csv')
        
        # condition to continue in case of no data
        if c.shape[0] == 0:
            continue
        c.to_csv(path+'Results/'+res_folder+str(n)+'_'+Hospital_site+'_'+Procedure_category+'_sliced_data.csv')
        
        # get and save the df with aggregated weekly counts
        d = get_table_with_weekly_counts(df, Hospital_site, Procedure_category)
        d.to_csv(path +'Results/'+res_folder+str(n)+'_'+Hospital_site+'_'+Procedure_category+'_weekly_counts.csv')
        
        # save the plot with time series endoscopy counts aggreagted weekly 
        p = d[['week_first_day','n_visits']].plot(x ='week_first_day', y = 'n_visits', title=Hospital_site + ': ' + Procedure_category)
        p.set_xlabel("Date")
        p.set_ylabel("Endoscopies per week")
        p.get_figure().savefig(path+'Results/'+res_folder+str(n)+'_'+Hospital_site+'_'+Procedure_category+'.pdf')
        p.get_figure().savefig(path+'Results/'+res_folder+str(n)+'_'+Hospital_site+'_'+Procedure_category+'.jpg', dpi=300)

        n+=1


























