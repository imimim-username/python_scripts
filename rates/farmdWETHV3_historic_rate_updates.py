import requests
import json
import time #for getting timestamp
import pandas as pd

import dotenv, os
from dune_client.client import DuneClient
#to upload CSV to dune


api_key = open("/home/imimim/mysite/alch/alchemy_api_key_arbitrum.txt", "r")
# get the alchemy_api_key

alchemy_key = api_key.read()
# read the key from the file

api_key.close()
# close the opened file

apiString = "https://arb-mainnet.g.alchemy.com/v2/" + alchemy_key
# constructs the alchemy api key

filePath = '/home/imimim/alchemix/protocol_stats/farmdWETHV3_rate_history.csv'
# csv location


'''def getStakingToken (yieldToken, block):

    dataStr = '0x72f702f3' # stakingToken function

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": yieldToken,
                "data": dataStr
            },
            "latest"
        ]
    }'''


# yieldToken = '0xf3b7994e4dA53E04155057Fd61dc501599d57877' # farmdWETHV3


def getSupplyRate (blockNumber):

    stakingToken = '0x04419d3509f13054f60d253E0c79491d9E683399'

    dataStr = '0xad2961a3' #supplyRate

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": stakingToken,
                "data": dataStr
            },
            blockNumber
        ]
    }

    rateResponse = requests.post(apiString, headers=headers, data=json.dumps(payload))

    rateInfo = rateResponse.json()

    rate = int(rateInfo['result'], 16)

    return rate / 1e27


def getBlock (timestamp):

    headers = {
        "Content-Type": "application/json"
    }
    #request headers

    print('Timestamp: ', timestamp)
    getBlockStr = 'https://api.arbiscan.io/api?module=block&action=getblocknobytime&timestamp=' + str(timestamp) + '&closest=before&apikey=YourApiKeyToken'

    blockNumber = requests.get(getBlockStr, headers=headers)

    blockNumber = blockNumber.json()

    # Pause execution for 5 seconds
    print('Pausing for 5 seconds because of rate limit')
    time.sleep(5)

    return hex(int(blockNumber['result']))

print('Loading rate history')
historyDF = pd.read_csv(filePath)

startingTime = max_timestamp = historyDF['timestamp'].max()

print('Last timestamp: ', startingTime)


timeInterval = 86400 # seconds in a day
currentTime = int(time.time())

timeLoop = startingTime + timeInterval

#counter = 0

rateHistory = []

while timeLoop < currentTime:

    blockNumber = getBlock(timeLoop)
    print('Timestamp: ', timeLoop)
    print('Block number: ', blockNumber)

    supplyRate = getSupplyRate(blockNumber)

    print('Supply rate: ', supplyRate)

    rateInfo = {
        'timestamp' : timeLoop,
        'supplyrate' : supplyRate
    }

    rateHistory.append(rateInfo)

    timeLoop += timeInterval

    #counter += 1

    #if counter >= 2:
     #   break

print('Rate history:')
print(rateHistory)



#convert to dataframe
df = pd.DataFrame(rateHistory)

print('Saving csv')
# Append dataframe to CSV
df.to_csv(filePath, mode='a', index=False, header=False)

# change the current working directory where .env file lives
os.chdir("/home/imimim/alchemix/arbitrum/")
# load .env file
dotenv.load_dotenv("dune.env")

# setup Dune Python client
dune = DuneClient.from_env()

# define path to your CSV file
csv_file_path = filePath

print('Uploading CSV to Dune')

with open(csv_file_path) as open_file:
    data = open_file.read()

    table = dune.upload_csv(
        data=str(data),
        description="farmdWETHV3 historic rate updates",
        table_name="farmdWETHV3_historic_rate_updates", # define your table name here
        is_private=False
    )


