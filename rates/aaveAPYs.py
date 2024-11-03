import requests

import dotenv, os
from dune_client.client import DuneClient
#to upload CSV to dune

import pandas as pd

from collections import defaultdict
from datetime import datetime, timedelta
import csv

from graphKey import returnKey

def getRates(startingTimestamp):
    apyRates = []

    moreToGo = True
    counter = 0

    while moreToGo == True:
        #graphURL = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum"
        graphApiKey = returnKey()

        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/DLuE98kEb5pQNXAcKFQGQgfSQ57Xdou4jnVbAEqMfy3B'
        # url for querying the graph

        query = """
        {
          reserveParamsHistoryItems(
            where: {reserve_: {aToken: "0x724dc807b04555b71ed48a6896b6f41593b8c637"}, timestamp_gte:""" + str(startingTimestamp + 86400) + """}
            orderBy: timestamp
            orderDirection: asc
            first: 1000
            skip: """ + str(counter * 1000) +"""
          ) {
            liquidityRate
            reserve {
              aToken {
                id
              }
            }
            timestamp
          }
        }
        """
        # query for aave apr history for the gfiven atoken after 1 April 2024

        data = {
            "query" : query
        }
        # puts the query into a usable data thingy for making a web request

        headers = {
            "Content-Type": "application/json"
        }
        #api call request headers

        print('Making request number ', str(counter + 1))
        queryResponse = requests.post(graphURL, json=data, headers=headers)

        queryData = queryResponse.json()

        try:
            apyRates.extend(queryData['data']['reserveParamsHistoryItems'])
            numberOfResponses = len(queryData['data']['reserveParamsHistoryItems'])
            if numberOfResponses < 1000:
                moreToGo = False
        except:
            print(queryData)
            moreToGo = False

        counter = counter + 1



    #print(apyRates)

    for x in apyRates:
        x['reserve'] = x['reserve']['aToken']['id']
        x['aToken'] = x.pop('reserve')
        x['liquidityRate'] = int(x['liquidityRate']) / (10 ** 27)
        #print(x)


    avgApyPerDay = defaultdict(list)

    for struct in apyRates:

        # Convert Unix timestamp to datetime object
        timestamp = datetime.utcfromtimestamp(struct['timestamp'])
        # Extract date (ignoring time component)
        date = timestamp.date()
        #date = int(datetime.datetime.combine(date, datetime.time()).timestamp())

        # Append liquidityRate to the list corresponding to the date
        avgApyPerDay[date].append(struct['liquidityRate'])

    avgApyStructList = []

    for date, liquidity_rates in avgApyPerDay.items():
        # Calculate the average liquidity rate
        average_liquidity_rate = sum(liquidity_rates) / len(liquidity_rates)

        # Convert date to Unix timestamp
        unix_timestamp = int(datetime.combine(date, datetime.min.time()).timestamp())


        # Create a dictionary representing the struct
        struct = {'date': date, 'timestamp': unix_timestamp, 'avgRate': average_liquidity_rate}

        # Append the struct to the list
        avgApyStructList.append(struct)

    for x in avgApyStructList:
        x.pop('date', None)

    return(avgApyStructList)

filePath = '/home/imimim/alchemix/arbitrum/aArbUSDCn_Rates.csv'
#where the CSV is being stored

# Define the list to store structs
aaveRates = []

# Open the CSV file and read its contents
with open(filePath, mode='r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Extract values from the CSV row
        unix_timestamp = int(row['timestamp'])
        average_liquidity_rate = float(row['avgRate'])

        # Create the struct
        struct = {'timestamp': unix_timestamp, 'avgRate': average_liquidity_rate}

        # Append the struct to avgApyStructList
        aaveRates.append(struct)

print(aaveRates)

# Find the maximum unix_timestamp value
maxTimestamp = max(aaveRates, key=lambda x: x['timestamp'])['timestamp']

toAdd = getRates(maxTimestamp)

#print(toAdd)

aaveRates.extend(toAdd)

print(aaveRates)

print('Creating CSV')

df = pd.DataFrame(aaveRates)
df.to_csv(filePath, index=False)

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
        description="Aave Arbitrum aArbUSDCn average daily APY rates",
        table_name="arbitrum_aave_aArbUSDCn_average_daily_apy_rates", # define your table name here
        is_private=False
    )
