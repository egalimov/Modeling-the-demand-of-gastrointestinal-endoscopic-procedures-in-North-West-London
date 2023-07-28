# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:25:03 2023

@author: EvgenyGalimov
"""


import pandas as pd

# load the data and preprocessing the data from 5 different tabs: referrals, rebookings, emergency, surveilance, removals - so that they could be combined in 1 table
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/Data/'

# referrals
referrals = pd.read_excel(path+'ChelWest_Endoscopy_2023_02_13_CW.xlsx', sheet_name='referrals')
referrals2 = referrals.iloc[6:referrals.shape[0], 1:referrals.shape[1]]
referrals2.columns = referrals2.iloc[0]
referrals2 = referrals2.drop(referrals2.index[0])
referrals2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
referrals2['Visit type'] = 'Referral'


# removals
removals = pd.read_excel(path+'ChelWest_Endoscopy_2023_02_13_CW.xlsx', sheet_name='removals')
removals2 = removals.iloc[6:removals.shape[0], 1:removals.shape[1]]
removals2.columns = removals2.iloc[0]
removals2 = removals2.drop(removals2.index[0])
removals2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
removals2['Visit type'] = 'Removal'


# rebookings
rebookings = pd.read_excel(path+'ChelWest_Endoscopy_2023_02_13_CW.xlsx', sheet_name='rebookings')
rebookings2 = rebookings.iloc[6:rebookings.shape[0], 1:rebookings.shape[1]]
rebookings2.columns = rebookings2.iloc[0]
rebookings2 = rebookings2.drop(rebookings2.index[0])
rebookings2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
rebookings2['Visit type'] = 'Rebooking'


# emergency
emergency = pd.read_excel(path+'ChelWest_Endoscopy_2023_02_13_CW.xlsx', sheet_name='emergency')
emergency2 = emergency.iloc[6:emergency.shape[0], 1:emergency.shape[1]]
emergency2.columns = emergency2.iloc[0]
emergency2 = emergency2.drop(emergency2.index[0])
emergency2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
emergency2['Visit type'] = 'Emergency'


# surveillance
surveillance = pd.read_excel(path+'ChelWest_Endoscopy_2023_02_13_CW.xlsx', sheet_name='surveillance')
surveillance2 = surveillance.iloc[6:surveillance.shape[0], 1:7]
surveillance2.columns = surveillance2.iloc[0]
surveillance2 = surveillance2.drop(surveillance2.index[0])
surveillance2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
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


### setting same names for the categories named differently
# fixing Hospital site
combined = combined.replace({'Hospital site': 'Chelsea and Westminster'}, 'CW')
combined = combined.replace({'Hospital site': 'West Middlesex'}, 'WM')
combined = combined.replace({'Hospital site': 'WMUH'}, 'WM')

# fixing Procedure category
combined = combined.replace({'Procedure category': 'OGD and Colon/Flexi '}, 'OGD and Colon/Flexi')
combined = combined.replace({'Procedure category': 'Flexi sigmoidoscopy'}, 'Flexible Sigmoidoscopy')
combined = combined.replace({'Procedure category': 'Flexi Sigmoidoscopy'}, 'Flexible Sigmoidoscopy')
combined = combined.replace({'Procedure category': 'Other '}, 'Other')
combined = combined.replace({'Procedure category': 'Flexible Sigmoidoscopy'}, 'Flexible_Sigmoidoscopy')
combined = combined.replace({'Procedure category': 'OGD and Colon/Flexi'}, 'OGD_and_Colon_Flexi')
combined = combined.replace({'Procedure category': 'Upper GI Endoscopy'}, 'Gastroscopy')




# get the list and counts for 'Procedure category': Other
combined['Procedure code'] = combined['Procedure code'].astype(str)
a = pd.pivot_table(combined,index=['Procedure category','Procedure code'])
a2 = combined[combined['Procedure category'] == 'Other' ][['Procedure code','Points']]
# adding index to get counts of unique rows
a2.reset_index(drop=True, inplace=True)
a2['index'] = a2.index
a2['Procedure code'].value_counts()
a2['Procedure code'].isna().sum()
# pivot table with unique row counts (index)
a4 = pd.pivot_table(a2,index=['Procedure code','Points'],aggfunc=lambda x: len(x.unique()))


# Replace 'Procedure category': Other to various categories based on 'Procedure code'
import copy
combined2 = copy.deepcopy(combined)
combined2['Procedure code'] = combined2['Procedure code'].astype(str)

for i in range(0, combined2.shape[0]):
    if ((combined2.iloc[i,3] == ' ')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'
    if ((combined2.iloc[i,3] == 'E499')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'
    if ((combined2.iloc[i,3] == 'G211')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Gastroscopy'
    if ((combined2.iloc[i,3] == 'G451')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Gastroscopy'
    if ((combined2.iloc[i,3] == 'G452')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'
    if ((combined2.iloc[i,3] == 'G802')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'
    if ((combined2.iloc[i,3] == 'J439')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'ERCP'
    if ((combined2.iloc[i,3] == 'J441')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'
    if ((combined2.iloc[i,3]== 'nan')&(combined2.iloc[i,4]=='Other')): combined2.iloc[i,4] = 'Remove'

# remove not needed categories
combined2 = combined2[combined2['Procedure category'] != 'Remove']


# saving the processed dataset
combined2.to_csv(path + '0_chelwest_combined.csv', index = False)




