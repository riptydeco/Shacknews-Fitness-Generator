#!/usr/bin/env python3

import json
import time
import requests
import urllib3
import json
#from yaspin import yaspin
import fileReader

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#spinner = yaspin()

#http_proxy = fileReader.jsonLoader('proxy') #only if needed
oauth_url = fileReader.jsonLoader('StravaURL')['oauth']
client_info = fileReader.jsonLoader('StravaClient')
access_key = fileReader.jsonLoader('StravaToken')

print('\n-- STRAVA API AUTHENTICATION --\n')

payload = {'client_id': client_info['client_id'],
           'client_secret': client_info['client_secret'],
           'refresh_token': access_key['refresh_token'],
           'grant_type': 'refresh_token',
           'f': 'json'
           }
 
current_time = time.time()

print('Checking Strava access token... ', end='')

if access_key['expires_at'] > current_time:
    #response = 'current key is still valid'
    print('current token is still valid')
    #access_token = access_key['access_token']

else:
    print('access token expired.  Fetching new token... ', end='')
    #spinner.start()
    #res = requests.post(oauth_url, data=payload, proxies=http_proxy, verify=False).json() #if network proxy required
    res = requests.post(oauth_url, data=payload, verify=False).json()
    #spinner.stop()
    #print(res)
    #access_token = access_key['access_token']
    #filename = '/Users/Craig/Documents/pythonApps/athleteAPI/files/StravaAccessToken.json'

    # with open(filename, 'w') as outfile:
    #     json.dump(res, outfile)
    fileReader.jsonWriter('StravaToken', res)
    #response = 'new key acquired'
    print('new token acquired')

print('\n-- STRAVA API AUTHENTICATION COMPLETE --\n')

