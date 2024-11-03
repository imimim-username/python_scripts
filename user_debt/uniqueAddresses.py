# This tries to use the subgraph to get all unique depositors in Alchemist

import requests
import json
import pandas as pd

import time
# to pause execution for debugging and things likt that, and to time how long the script takes

from graphKey import returnKey

from deposit_addresses import uniqueDepositAddresses

def pinataPin (pinata_file_name, jsonData):
# pins a json to pinata based on file name and json data being passed

    api_key = open("/home/imimim/alchemix/user_debt/pinata_api_key.txt", "r")
    # get the pinata_api_key

    pinata_key = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": pinata_key
    }
    # pinata api call request headers

    request_data = {
        "pinataOptions": {
            "cidVersion": 1
         },
         "pinataMetadata": {
            "name": pinata_file_name
         },
         "pinataContent": jsonData
    }
    # api request payload for writing debt values to pinata

    pinata_json_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    # pinata endpoint for posting json

    print("Pinning new user debt file to pinata")
    pinata_post = requests.post(pinata_json_url, headers = request_headers, data=json.dumps(request_data))
    # calls the pinata API for writing debt values to pinata

    result = pinata_post.json()
    # turns the result into a usable json

    print("Pinata post result")
    print(result)

def pinataDelete (fileHash):
# unpins a file on pinata based on its hash

    api_key = open("/home/imimim/alchemix/user_debt/pinata_api_key.txt", "r")
    # get the pinata_api_key

    pinata_key = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": pinata_key
    }
    # pinata api call request headers
    deleteURL = "https://api.pinata.cloud/pinning/unpin/" + fileHash
    # building the url to unpin old file on pinata

    print("Unpinning old file")
    unpin = requests.delete(deleteURL, headers = request_headers)
    # unpin old user debt file in pinata
    print(unpin.text)

def pinataHash (pinata_file_name):
# looks up a file hash in pinata based on the file name

    api_key = open("/home/imimim/alchemix/user_debt/pinata_api_key.txt", "r")
    # get the pinata_api_key

    pinata_key = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    request_headers = {
        "Content-Type": "application/json",
        "Authorization": pinata_key
    }
    # pinata api call request headers

    find_file_string_1 = "https://api.pinata.cloud/data/pinList?includeCount=false&metadata[name]="
    find_file_string_2 = "&status=pinned&pageLimit=1"
    # these two strings are used with the file name to search for the file name on pinata

    find_file_url = find_file_string_1 + pinata_file_name + find_file_string_2
    # the full string for finding the file on pinata

    print("Looking up " + pinata_file_name + " file on pinata")
    pinata_file_location = requests.get(find_file_url, headers = request_headers)
    # looking for pre-existing file on pinata

    pinata = pinata_file_location.json()
    # gets a json of pinata file location

    fileHash = pinata["rows"][0]["ipfs_pin_hash"]
    # ipfs file hash of the existing file.

    return fileHash


def graphCall (networkInfo):
# calls subgraph to get the depositors
# Uses multiplier to determine from where to start the values

    # graphEndpoint = 'https://subgraph.satsuma-prod.com/aa9bbeae54d2/alchemix--802384/alchemix-v2/api'

    counter = 0
    shouldContinue = True

    tempDepositAddresses = []
    #instantiating blank address struct

    while shouldContinue == True:

        print('Counter: ', counter)
        multiplier = counter * 1000
        # queryPayload = '{{\"query\":\"{{\\r\\n alchemistDepositEvents(\\r\\n orderBy: timestamp\\r\\n orderDirection: asc\\r\\n skip: {}\\r\\n first: 1000\\r\\n ) {{\\r\\n recipient\\r\\n }}\\r\\n}}\"}}'.format(multiplier)
        query = '''
            {
                alchemistDepositEvents(
                    orderBy: timestamp
                    orderDirection: asc
                    skip:''' + str(multiplier) + '''
                    first: 1000
                ) {
                    recipient
                }
            }
        '''

        queryPayload = {
            'query' : query
        }

        headers = {
            "Content-Type": "application/json"
        }


        print('Calling endpoint')
        response = requests.post(networkInfo['graphEndpoint'], json=queryPayload, headers=headers)

        responseInfo = response.json()

        responseInfo = responseInfo['data']

        responseInfo = responseInfo['alchemistDepositEvents']

        y = 0
        for x in responseInfo:
            print('Adding: ', x)
            tempThing = {
                'address': x['recipient']
            }
            tempDepositAddresses.append(tempThing)
            y = y + 1

        counter = counter + 1

        if y == 1000:
            shouldContinue = True
        else:
            shouldContinue = False

    return tempDepositAddresses


graphApiKey = returnKey()

deployments = [
    {
        "network" : "mainnet",
        "graphEndpoint" : 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/GJ9CJ66TgbJnXcXGuZiSYAdGNkJBAwqMcKHEvfVmCkdG',
        'depositAddresses' : [],
        'pinataFile' : 'mainnet_user_debt_addresses.json'
    },
    {
        'network' : 'optimism',
        # 'graphEndpoint' : 'https://api.thegraph.com/subgraphs/name/alchemix-finance/alchemix_v2_optimisim', # THIS IS DEPRECATED
        # 'graphEndpoint' : 'https://subgraph.satsuma-prod.com/de91695d5fb0/alchemix--802384/alchemix_v2_optimisim/version/female_white_earwig/api', # this is currently deploying
        #'graphEndpoint' : 'https://api.goldsky.com/api/public/project_clweyetqu7b0o01uldfi32lnh/subgraphs/optimism-subgraph/1.0.0/gn', # this works, but was hitting monthly limit
        'graphEndpoint' : 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/GYBJ8wsQFkSwcgCqhaxnz5RU2VbgedAkWUk2qx9gTnzr',
        'depositAddresses' : [],
        'pinataFile' : 'optimism_user_debt_addresses.json'
    },
    {
        'network' : 'arbitrum',
        # 'graphEndpoint' : 'https://subgraph.satsuma-prod.com/aa9bbeae54d2/alchemix--802384/alchemix-v2-arb/version/v0.0.2/api',
        # 'graphEndpoint' : 'https://api.goldsky.com/api/public/project_cltwyhnfyl4z001x17t5odo5x/subgraphs/alchemix-arb/1.0.0/gn',
        # 'graphEndpoint' : 'https://api.goldsky.com/api/public/project_clweyetqu7b0o01uldfi32lnh/subgraphs/arbitrum-subgraph/1.0.0/gn', # this works, but was hitting monthly limit
        'graphEndpoint' : 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/Dgjyhh69XooHPd4JjvT3ik9FaGAR3w7sUSQyQ1YDakGp',
        'depositAddresses' : [],
        'pinataFile' : 'arbitrum_user_debt_addresses.json'
    }
]


'''for x in deployments:
    print(x['pinataFile'])'''
start = time.time()
print('Starting timer')

#getting latest addresses
uniqueDepositAddresses()

for x in deployments:
    #for z in graphCall(x):
    #    x['depositAddresses'].append(z)

    fileName = x['pinataFile']
    print('File name: ', fileName)
    oldHash = pinataHash(fileName)
    print('Old hash: ', oldHash)
    # time.sleep(10)

    '''x['depositAddresses'] = graphCall(x)

    print('Length of all addresses: ', len(x['depositAddresses']))
    # time.sleep(10)

    uniqueAddresses = []

    for x in x['depositAddresses']:

        if x not in uniqueAddresses:
            print('Adding unique address', x)
            uniqueAddresses.append(x)
        else:
            print(x, ' is not unique and is being skipped')'''

    uniqueCsvPath = '/home/imimim/alchemix/user_debt/unique_' + x['network'] + '_addresses.csv'

    dfAddresses = pd.read_csv(uniqueCsvPath)

    dfAddresses = dfAddresses.rename(columns={'recipient': 'address'})
    uniqueAddresses = []

    for index, row in dfAddresses.iterrows():
        addressData = {
            'address' : row['address']
        }

        uniqueAddresses.append(addressData)

    #print(uniqueAddresses)
    print('Length of unique addresses: ', len(uniqueAddresses))
    # time.sleep(10)

    '''print('Changing \"recipient\" to \"address\"')
    for y in uniqueAddresses:
    # changing 'recipient' to 'address'
        if 'recipient' in y:
            y['address'] = y.pop('recipient')'''

    # time.sleep(10)
    # print(uniqueAddresses)
    # print('Converting to JSON')

    # jsonAddresses = json.dumps(uniqueAddresses, ensure_ascii=False)
    # jsonAddresses = json.dumps(uniqueAddresses)

    # time.sleep(10)
    pinataDelete(oldHash)
    # time.sleep(10)
    pinataPin(fileName,uniqueAddresses)
    # time.sleep(10)

end = time.time()

duration = end - start

print("This thing took")
print(duration)
print("seconds to execute")
