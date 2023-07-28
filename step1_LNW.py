# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:25:03 2023

@author: EvgenyGalimov
"""


import pandas as pd
from datetime import datetime
import numpy as np


# load the data and preprocessing the data from 5 different tabs: referrals, rebookings, emergency, surveilance, removals - so that they could be combined in 1 table
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/Data/'
filename = 'Endoscopy historical data request - LNW v2.xlsx'


# referrals
referrals = pd.read_excel(path+filename, sheet_name='referrals')
referrals2 = referrals.iloc[6:referrals.shape[0], 1:referrals.shape[1]]
referrals2.columns = referrals2.iloc[0]
referrals2 = referrals2.drop(referrals2.index[0])
referrals2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points', 'Patients number']
referrals2['Visit type'] = 'Referral'


# removals
removals = pd.read_excel(path+filename, sheet_name='removals')
removals2 = removals.iloc[6:removals.shape[0], 1:removals.shape[1]]
removals2.columns = removals2.iloc[0]
removals2 = removals2.drop(removals2.index[0])
removals2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points', 'Patients number']
removals2['Visit type'] = 'Removal'


# rebookings
rebookings = pd.read_excel(path+filename, sheet_name='rebookings')
rebookings2 = rebookings.iloc[6:rebookings.shape[0], 1:rebookings.shape[1]]
rebookings2.columns = rebookings2.iloc[0]
rebookings2 = rebookings2.drop(rebookings2.index[0])
rebookings2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points', 'Patients number']
rebookings2['Visit type'] = 'Rebooking'


# emergency
emergency = pd.read_excel(path+filename, sheet_name='emergency')
emergency2 = emergency.iloc[6:emergency.shape[0], 1:emergency.shape[1]]
emergency2.columns = emergency2.iloc[0]
emergency2 = emergency2.drop(emergency2.index[0])
emergency2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points', 'Patients number']
emergency2['Visit type'] = 'Emergency'


# surveillance
surveillance = pd.read_excel(path+filename, sheet_name='surveillance')
surveillance2 = surveillance.iloc[6:surveillance.shape[0], 1:surveillance.shape[1]]
surveillance2.columns = surveillance2.iloc[0]
surveillance2 = surveillance2.drop(surveillance2.index[0])
surveillance2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points', 'Patients number']
surveillance2['Visit type'] = 'Surveillance'


# printing value counts
referrals2['Hospital site'].value_counts()
removals2['Hospital site'].value_counts()
rebookings2['Hospital site'].value_counts()
emergency2['Hospital site'].value_counts()
surveillance2['Hospital site'].value_counts()

referrals2['Procedure category'].value_counts()
removals2['Procedure category'].value_counts()
rebookings2['Procedure category'].value_counts()
emergency2['Procedure category'].value_counts()
surveillance2['Procedure category'].value_counts()






###  COMBINING
combined = pd.concat([referrals2, removals2, rebookings2, emergency2, surveillance2], axis = 0)


# check if there are missing Dates
ind = []
for i in range(0, combined.shape[0]):
    #print(i)
    if ( (type(combined.iloc[i,0]) == pd._libs.tslibs.timestamps.Timestamp) or (type(combined.iloc[i,0]) == datetime) ):
        ind.append(i)

combined=combined[combined.index.isin(ind)]

referrals2.shape[0]+removals2.shape[0]+rebookings2.shape[0]+emergency2.shape[0]+surveillance2.shape[0]


# fixing Procedure category
combined = combined.replace({'Procedure category': 'other'}, 'Other')
combined = combined.replace({'Procedure category': 'Flexi sigmoidoscopy'}, 'Flexible Sigmoidoscopy')

combined = combined[combined['Procedure category'] != 'Exclude - poor DQ']


# get the list and counts for 'Procedure category': Gastroscopy
a2 = combined[combined['Procedure category'] == 'Gastroscopy' ][['Procedure code','Points', 'Patients number']]
# adding index to get counts of unique rows
a2.reset_index(drop=True, inplace=True)
a2['index'] = a2.index
a2['Procedure code'].value_counts()
a2['Procedure code'].isna().sum()
# pivot table with unique row counts (index)
a4 = pd.pivot_table(a2,index=['Procedure code','Points', 'Patients number'],aggfunc=lambda x: len(x.unique()))


# get the list and counts for 'Procedure category': Gastroscopy
a2 = combined[combined['Procedure category'] == 'Colonoscopy' ][['Procedure code','Points', 'Patients number']]
# adding index to get counts of unique rows
a2.reset_index(drop=True, inplace=True)
a2['index'] = a2.index
a2['Procedure code'].value_counts()
a2['Procedure code'].isna().sum()
# pivot table with unique row counts (index)
a4 = pd.pivot_table(a2,index=['Procedure code','Points', 'Patients number'],aggfunc=lambda x: len(x.unique()))



# get the list and counts for 'Procedure category': Gastroscopy
a2 = combined[combined['Procedure category'] == 'Flexible Sigmoidoscopy' ][['Procedure code','Points', 'Patients number']]
# adding index to get counts of unique rows
a2.reset_index(drop=True, inplace=True)
a2['index'] = a2.index
a2['Procedure code'].value_counts()
a2['Procedure code'].isna().sum()
# pivot table with unique row counts (index)
a4 = pd.pivot_table(a2,index=['Procedure code','Points', 'Patients number'],aggfunc=lambda x: len(x.unique()))



# get the list and counts for 'Procedure category': Other
combined['Procedure code'] = combined['Procedure code'].astype(str)
a = pd.pivot_table(combined,index=['Procedure category','Procedure code', 'Patients number'])
a2 = combined[combined['Procedure category'] == 'Other' ][['Procedure code','Points', 'Patients number']]
# adding index to get counts of unique rows
a2.reset_index(drop=True, inplace=True)
a2['index'] = a2.index
a2['Procedure code'].value_counts()
a2['Procedure code'].isna().sum()
# pivot table with unique row counts (index)
a4 = pd.pivot_table(a2,index=['Procedure code','Points', 'Patients number'],aggfunc=lambda x: len(x.unique()))


# Replace 'Procedure category': Other to various categories based on 'Procedure code'
combined2 = copy.deepcopy(combined)
combined2['Procedure code'] = combined2['Procedure code'].astype(str)
combined2 = combined2[combined2['Procedure category'] == 'Other']

# load the file from Dr Krishna where he specified what procedure codes to include in the analysis
cond = pd.read_csv(path+'3_LMW_others_cat_points_counts_Krishna.csv')
cond_G = cond[cond['type'] == 'G']['Procedure code'].to_list()
cond_S = cond[cond['type'] == 'S']['Procedure code'].to_list()
cond_C = cond[cond['type'] == 'C']['Procedure code'].to_list()
cond_E = cond[cond['type'] == 'E']['Procedure code'].to_list()
cond_CAP = cond[cond['type'] == 'CAP']['Procedure code'].to_list()
cond_G_C = cond[cond['type'] == 'G+C']['Procedure code'].to_list()
cond_G_S = cond[cond['type'] == 'G+S']['Procedure code'].to_list()


# renaming procedure types according to Krishna's recommendations
for i in range(0, combined2.shape[0]):
    for j in range(0, len(cond_G)):
        if ((combined2.iloc[i,3] == cond_G[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Gastroscopy'

    for j in range(0, len(cond_S)):
        if ((combined2.iloc[i,3] == cond_S[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Flexible Sigmoidoscopy'

    for j in range(0, len(cond_C)):
        if ((combined2.iloc[i,3] == cond_C[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Colonoscopy'

    for j in range(0, len(cond_E)):
        if ((combined2.iloc[i,3] == cond_E[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'ERCP'

    for j in range(0, len(cond_G_C)):
        if ((combined2.iloc[i,3] == cond_G_C[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Gastroscopy and colonoscopy'

    for j in range(0, len(cond_G_S)):
        if ((combined2.iloc[i,3] == cond_G_S[j])&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Gastroscopy and Flexible Sigmoidoscopy'



combined3 = combined[combined['Procedure category'] != 'Other']
combined2_2 = combined2[combined2['Procedure category'] != 'Other']
combined2_3 = combined2[combined2['Procedure category'] == 'Other']
combined2_3.to_csv(path + '3_LMW_excluded_rows.csv')


# saving the table with excluded procedure codes
co_list_other = combined2_3['Procedure code'].value_counts()
co_list_other = pd.DataFrame(co_list_other)
co_list_other['index'] = co_list_other.index
co_list_other.to_csv(path + '3_LMW_excluded_rows__Cat_list.csv', index = False)

# combining data without excluded procedure codes
combined5 = pd.concat([combined3, combined2_2], axis = 0)


###
# for rows with multiple patients - repeat and insert that row the number of times = number of patients 
combined5['Patient#'] = 1

# function to insert a row
def insert_row(idx, df, df_insert):
    dfA = df.iloc[:idx, ]
    dfB = df.iloc[idx:, ]

    df = dfA.append(df_insert).append(dfB).reset_index(drop = True)

    return df

# get those rows with >1 patients 
combined5_1 = combined5[ combined5['Patients number'] != 1 ]
# # get those rows with 1 patient 
combined5_2 = combined5[ combined5['Patients number'] == 1 ]

# multiply rows with >1 patients 
combined5_1_len = combined5_1.shape[0]
for i in range(0, combined5_1_len):
    n = combined5_1.iloc[i, 6]
   
    for j in range(1, n):
        
        combined5_1 = insert_row(combined5_1.shape[0], combined5_1, combined5_1.iloc[i,:])
        combined5_1.iloc[-1,8] = j+1 

# sort values
combined5_1 = combined5_1.sort_values(['Date','Patients number','Patient#'], ascending = [True, False, True])

# combine df with 1 patient per row and updated df2 with multiplied rows
combined6 = pd.concat([combined5_1, combined5_2], axis = 0)




### setting same names for the categories named differently
combined6 = combined6.replace({'Procedure category': 'Gastroscopy and colonoscopy'}, 'Gastroscopy')
combined6 = combined6.replace({'Procedure category': 'Gastroscopy and Flexible Sigmoidoscopy'}, 'Gastroscopy')

combined7 = copy.deepcopy(combined6)
combined7['Date'] = combined7['Date'].astype(str)
combined7.reset_index(drop=True, inplace=True)

# check if there are missing Dates
ind = []
for i in range(0, combined7.shape[0]):
    print(i)
    try:
        type(combined7.iloc[i,0])
        combined7.iloc[i,0] = pd.to_datetime(combined7.iloc[i,0], format = '%Y-%m-%d')
        ind.append(i)
    except:
        print("An exception occurred.   i: " + str(i))
combined8=combined7[combined7.index.isin(ind)]


# split the dataset into LNW BCSP and LNW
# get the data related to BCSP
a = combined[combined['Date2'].isna() ] 
a.to_csv('C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/Data/LNW_all_cdoes.csv')

a = combined['Procedure code'].value_counts()
a = pd.DataFrame(a)
a['index'] = a.index
a2 = a[a['index'].str.contains('BCSC')]
a2.to_csv('C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/Data/LNW_BCSP_codes.csv')



LNW_BCSP_codes = pd.read_csv(path + 'LNW_BCSP_codes.csv')
LNW_BCSP_codes = LNW_BCSP_codes[~LNW_BCSP_codes.isin([np.nan, np.inf, -np.inf]).any(1)]
LNW_BCSP_col_codes = LNW_BCSP_codes[LNW_BCSP_codes['Procedure code'].str.contains('Colonoscopy')]

combined9 = combined8[~combined8['Procedure code'].isin(LNW_BCSP_col_codes['Procedure code'].to_list())]
dLNW_BCSP = combined8[combined8['Procedure code'].isin(LNW_BCSP_col_codes['Procedure code'].to_list())]
dLNW_BCSP.to_csv(path + '3_LMW_BCSP.csv', index = False)


# saving the processed dataset
combined9.to_csv(path + '3_LMW_combined.csv', index = False)

















