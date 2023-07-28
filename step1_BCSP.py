# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 15:25:03 2023

@author: EvgenyGalimov
"""


import pandas as pd
from datetime import datetime

# load the data and preprocessing the data from 5 different tabs: referrals, rebookings, emergency, surveilance, removals - so that they could be combined in 1 table
path = 'C:/Users/EvgenyGalimov/OneDrive - Imperial College Health Partners/Documents/Docs/22_Endoscopy_forcasting_demand/Data/'
filename = 'Copy of Endoscopy historical data request 2023 02 13_BCSP.xlsx'

# referrals
referrals_1 = pd.read_excel(path+filename, sheet_name='referrals colons')

referrals_1_2 = referrals_1.drop(['Unnamed: 2'], axis=1)
referrals_1_2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
referrals_1_2['Visit type'] = 'Referral'

referrals_2 = pd.read_excel(path+filename, sheet_name='referals CTC')
referrals_2_2 = referrals_2.drop(['Unnamed: 2'], axis=1)
referrals_2_2.insert(3, 'Procedure code', '')
referrals_2_2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
referrals_2_2['Visit type'] = 'Referral'

referrals_3 = pd.read_excel(path+filename, sheet_name='referrals flexi sig')
referrals_3.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
referrals_3['Visit type'] = 'Referral'
referrals2 = pd.concat([referrals_1_2, referrals_2_2, referrals_3], axis = 0, sort=False)


# removals
removals = pd.read_excel(path+filename, sheet_name='removals')
removals2 = removals.iloc[:, 0:5]
removals2['Points'] = ''
removals2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
removals2['Visit type'] = 'Removal'


# rebookings
rebookings = pd.read_excel(path+filename, sheet_name='rebookings')
rebookings2 = rebookings.iloc[6:rebookings.shape[0], 1:rebookings.shape[1]]
rebookings2.columns = rebookings2.iloc[0]
rebookings2 = rebookings2.drop(rebookings2.index[0])
rebookings2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
rebookings2['Visit type'] = 'Rebooking'


# emergency
emergency = pd.read_excel(path+filename, sheet_name='emergency')
emergency2 = emergency.iloc[6:emergency.shape[0], 1:emergency.shape[1]]
emergency2.columns = emergency2.iloc[0]
emergency2 = emergency2.drop(emergency2.index[0])
emergency2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category', 'Points']
emergency2['Visit type'] = 'Emergency'


# surveillance
surveillance = pd.read_excel(path+filename, sheet_name='surveillance')
surveillance2 = surveillance
surveillance2.columns = ['Date', 'Patient age', 'Hospital site',
       'Procedure code', 'Procedure category']
surveillance2['Points'] = ''
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
combined = combined.replace({'Hospital site': 'IMPERIAL'}, 'Imperial')

# fixing Procedure category
combined = combined.replace({'Procedure category': 'Flexible Sigmoiodoscopy Bowel Scope'}, 'Flexible Sigmoidoscopy')
combined = combined.replace({'Procedure category': 'FS Screening'}, 'Flexible Sigmoidoscopy')
combined = combined.replace({'Procedure category': 'Colon'}, 'Colonoscopy')


# removing missing/erroneous Date valeus
combined = combined.reset_index(drop=True)

# getting a list with date is in the right format
ind = []
for i in range(0, combined.shape[0]):
    print(i)
    if ( (type(combined.iloc[i,0]) == pd._libs.tslibs.timestamps.Timestamp) or (type(combined.iloc[i,0]) == datetime) ):
        ind.append(i)

# getting the dataset with dates in the right format
combined_clean=combined[combined.index.isin(ind)]
print( type(combined_clean.iloc[0,0])  )
c = 0
for i in range(0, combined_clean.shape[0]-1):   
    if type(combined_clean.iloc[i+1,0]) != type(combined_clean.iloc[i+1,0]):
        print(c, type(combined_clean.iloc[i+1,0])  )
        c+=1


# saving the processed dataset
combined_clean.to_csv(path + '4_BCSP_combined.csv', index = False)


