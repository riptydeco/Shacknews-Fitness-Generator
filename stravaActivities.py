#!/usr/bin/env python3

#issues with package installs.  have to use: sudo python3 -m pip install yaspin

import requests
import urllib3
import time
import datetime
import calendar
import json
import pandas
import os
pandas.options.mode.chained_assignment = None # default = 'warn'
from yaspin import yaspin
import fileReader
import math

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

shackPostBuffer = ''
shackPost = 'y{Sundays are for Cycling}y]\n'
shackPost += 's[Witness the Fitness]s\n\n'

# Week is from the day the process is run
# Would be better if it found the actual start and end dates of the current week
WeekStart = datetime.date.today() - datetime.timedelta(days=6)
WeekEnd = datetime.date.today().strftime("%m/%d/%Y")
shackPost += 'Date range: ' + WeekStart.strftime("%m/%d/%Y") + ' - ' + WeekEnd + '\n\n'


#spinner = yaspin()
#os.system('clear')

def clear():

    _ = os.system('clear')

clear()

print('\n\n----------------')
print('STARTING NEW RUN AT...', datetime.datetime.now())
print('----------------\n')

#Validate and update Strava credentials

import stravaAuthN

#http_proxy = fileReader.jsonLoader('proxy') #only needed behind firewall
activities_url = fileReader.jsonLoader('StravaURL')['activities']
#client_info = fileReader.jsonLoader('StravaClient')
access_token = fileReader.jsonLoader('StravaToken')['access_token']
print('Activities API is', activities_url)

print('\n-- STRAVA ATHLETE DATA RETRIEVAL --\n')

yearstart = yearstart = datetime.datetime.now().date().replace(month=1, day=1)
YearDays = datetime.datetime.now().timetuple().tm_yday
today = datetime.date.today()
oneweek = datetime.timedelta(days=6)
LW = today - oneweek
print('Current date is ' + str(today))
time_object = time.strptime(str(yearstart), '%Y-%m-%d')
after_date = time.mktime(time_object)

param = {'access_token': access_token,
        #'before': datetime.datetime(2022, 1,10, 0, 0).timestamp(),
        #'after':  datetime.datetime(2022, 1,8, 0, 0).timestamp(),
        'after': after_date
        #'per_page': 200
        #,'page': 1
        }

print('Requesting data from ' + str(yearstart))

with yaspin(text='Retrieving Strava activities data...', timer=True) as sp:
    #my_dataset = requests.get(activities_url, params=param, proxies=http_proxy).json()
    my_dataset = requests.get(activities_url, params=param).json()
    sp.stop()

print('Retrieving Strava activities data... done')

print('Creating dataset... ', end='')
df = pandas.json_normalize(my_dataset)
df.to_csv('/Users/Craig/Documents/pythonApps/athleteAPI/files/Activities.csv')
print('done')

### MAKE TIME ADJUSTMENTS FOR EASIER PROCESSING ###
#Time zone adjustments

print('Adjusting time from GMT to local... ', end='')

df['localtimeepoch'] = ((pandas.to_datetime(df['start_date'], format='%Y-%m-%dT%H:%M:%SZ', errors='ignore') - pandas.Timestamp("1970-01-01")) // pandas.Timedelta('1s')) + df['utc_offset']
df['localtimets'] = pandas.to_datetime(df['localtimeepoch'], unit='s')
df['localtimedt'] = df['localtimets'].dt.strftime('%Y-%m-%d')
df.sort_values(by='localtimets', inplace=True, ascending=True)
print('done')

#Convert elapsed time to HH:MM
print('Calculating activity durations... ', end='')
df['elapsed_minutes'] = round(df['elapsed_time'] / 60)
df = df.astype({'elapsed_minutes': int})
df['elapsed_hhmm'] = pandas.to_datetime(df.elapsed_minutes, unit='m').dt.strftime('%H:%M')
print('done')

#PRINT AN ORDERED LIST OF ALL ACTIVITIES

print('\n-- ACTIVITY SUMMARY --\n')
#print(df[['type','start_date', 'elapsed_time']])

#print(df[['localtimedt', 'type', 'elapsed_time']])
# elapsed time to minutes is: '{:02d}:{:02d}'.format(*divmod(minutes, 60))
#print(df['localtimedt'].value_counts())

tyCount = len(pandas.unique(df['localtimedt']))
dftw = df[(pandas.to_datetime(df.localtimedt).dt.date >= LW)]
twCount = len(pandas.unique(dftw['localtimedt']))

#print('Active Days: ', end='', sep='')
#print('This week: ', twCount, '/7. ', end='', sep='')
#print('This year: ', tyCount, '/', datetime.datetime.now().timetuple().tm_yday, '\n', sep='')

shackPostBuffer = 'Active days: ' + 'This week: ' + str(twCount) + '/7.' + ' This year: ' + str(tyCount) + '/' + str(datetime.datetime.now().timetuple().tm_yday) + '\n'
print(shackPostBuffer)
shackPost += shackPostBuffer


# dftw.rename(columns={'type' : 'Activity', 'localtimedt' : 'Date', 'elapsed_hhmm': 'Duration'}, inplace=True)
# df2 = df.rename({'a': 'X', 'b': 'Y'}, axis=1)  # new method
dftw.rename({'type' : 'Activity', 'localtimedt' : 'Date', 'elapsed_hhmm': 'Duration'}, axis=1, inplace=True)
#print(dftw.to_string(columns=['Date', 'Activity', 'Duration'], index=False))
shackPostBuffer = '\n' + dftw.to_string(columns=['Date', 'Activity', 'Duration'], index=False)
print(shackPostBuffer)
shackPost += shackPostBuffer
# print(dftw.groupby(['Activity'])['elapsed_time'].sum())
#dfsum = pandas.DataFrame(columns=['Activity', 'TotalTime'])
#dfsum = dftw.groupby(['Activity'])['elapsed_time'].sum()
# dfsum.columns(['Activity', 'Total Time'])
# dfsum.rename(index={1: "Activity", 1: "Total Time"})
# print(dfsum)
# dfsum['elapsed_minutes'] = round(dfsum['elapsed_time'] / 60)
# dfsum = dfsum.astype({'elapsed_minutes': int})
# dfsum['Total Time'] = pandas.to_datetime(dfsum.elapsed_minutes, unit='m').dt.strftime('%H:%M')
# print(dfsum.to_string(columns=['Activity', 'Total Time'], index=False))

shackPostBuffer = '\n\nActivity Totals\n---------------\n'
print(shackPostBuffer)
shackPost += shackPostBuffer

dfsum = dftw.groupby(['Activity'])['elapsed_time'].sum()
#print(dfsum)
#dfsum['Ride'] = round(dfsum['Ride'] / 60)
#print(dfsum)
# dfsum = dfsum.astype({'RideTime': int})
# dfsum['Ride'] = pandas.to_datetime(dfsum.Ride, unit='m').dt.strftime('%H:%M')
minutes = math.trunc((dfsum['Ride']/60) % 60)
hours = math.trunc((dfsum['Ride']/3600) % 60)
#print('Cycling:  ','%d:%02d' % (hours, minutes), ' | Total output: ', round(dftw[dftw['Activity']=='Ride']['kilojoules'].sum()), ' kJ', sep='')
shackPostBuffer = 'Cycling:  ' + '%d:%02d' % (hours, minutes) + ' | Total output: ' + str(round(dftw[dftw['Activity']=='Ride']['kilojoules'].sum())) + ' kJ'
print(shackPostBuffer)
shackPost += shackPostBuffer

minutes = math.trunc((dfsum['Run']/60) % 60)
hours = math.trunc((dfsum['Run']/3600) % 60)
#print('Running:  ','%d:%02d' % (hours, minutes), ' | Total distance: ', round(dftw[dftw['Activity']=='Run']['distance'].sum()/2200,1), ' mi', sep='')
shackPostBuffer = '\nRunning:  ' + '%d:%02d' % (hours, minutes) + ' | Total output: ' + str(round(dftw[dftw['Activity']=='Ride']['kilojoules'].sum())) + ' kJ'
print(shackPostBuffer)
shackPost += shackPostBuffer

minutes = math.trunc((dfsum['WeightTraining']/60) % 60)
hours = math.trunc((dfsum['WeightTraining']/3600) % 60)
#print('Strength: ','%d:%02d' % (hours, minutes), ' | Total weight: ', sep='')
shackPostBuffer = '\nStrength:  ' + '%d:%02d' % (hours, minutes) + ' | Total output: ' + str(round(dftw[dftw['Activity']=='Ride']['kilojoules'].sum())) + ' kJ'
print(shackPostBuffer)
shackPost += shackPostBuffer

#print(dfsum.columns.values.tolist())

minutes = math.trunc(((dfsum['Ride'] + dfsum['Run'] + dfsum['WeightTraining']) / 60) % 60)
hours = math.trunc(((dfsum['Ride'] + dfsum['Run'] + dfsum['WeightTraining']) / 3600) % 60)
#print('Total:','%d:%02d' % (hours, minutes))
shackPostBuffer = '\nTotal: ' + '%d:%02d' % (hours, minutes)
print(shackPostBuffer)
shackPost += shackPostBuffer

# dfsum = dfsum.to_frame()
# dfsum['elapsed_time'] = dfsum['elapsed_time'] / 60
# print(dfsum)

# dfsum = dfsum.to_dict()
# print(dfsum)
#with open('/Users/craig.jones/Documents/zzPersonal/StravaApi/sumtest.txt', 'w') as outfile:
#     json.dump(dfsum, outfile)

print('\n-- END ACTIVITY SUMMARY --\n')


print('\n-- RUNNING ACTIVITIES --\n')

##rundf = dftw[(dftw.Activity == 'Run')]
#print(dftw[(dftw.Activity == 'Run')].to_string(columns=['Activity','Date', 'elapsed_time', 'Duration', 'distance'], index=False)) 

print('\n-- CYCLING ACTIVITIES --\n')

#undf = df[(df.type == 'Ride')]
#print(dftw[(dftw.Activity == 'Ride')].to_string(columns=['Activity','Date', 'elapsed_time', 'Duration', 'distance'], index=False))

# print(rundf[['type','start_date', 'elapsed_time', 'distance']])
 
# print(df['type'].value_counts())
# print(df.groupby('type')['elapsed_time'].sum()/60)

#print(df[['localtimedt', 'type', 'elapsed_time']])

# print(df.nunique)

filename = '/Users/Craig/Documents/pythonApps/athleteAPI/output/shackFile.txt'
with open(filename, 'w') as shackFile:
    #shackFile.write('y{Sundays are for Cycling}y]\n')
    #shackFile.write('s[Witness the Fitness]s\n')
    shackFile.write(shackPost)
