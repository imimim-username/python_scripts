import requests

import dotenv, os
from dune_client.client import DuneClient
#to upload CSV to dune

import pandas as pd
from datetime import datetime, timezone

# Get the current time in UTC
current_utc_time = datetime.now(timezone.utc)

# Extract the hour as an integer
current_utc_hour = current_utc_time.hour

timeChecker = current_utc_hour % 6

print('Timecheck: ', timeChecker)

if timeChecker == 0:
# only do this 4 times per day

    baseURL = 'https://eth-api.lido.fi/v1/protocol/steth/apr?page='

    wstethRates = []

    counter = 1

    shouldContinue = True

    while shouldContinue:

        requestStr = baseURL + str(counter)

        rates = requests.get(requestStr)

        rates = rates.json()

        page = rates['pagination']['page']

        pageCount = rates['pagination']['pageCount']

        print(rates)
        print(page)
        print(pageCount)

        wstethRates.extend(rates['data'])

        if int(page) == int(pageCount):
            shouldContinue = False

        if counter == int(pageCount):
            shouldContinue = False

        counter = counter + 1

    filePath = '/home/imimim/alchemix/arbitrum/wstETH_Rates.csv'
    #where the CSV is being stored

    print('Creating CSV')

    df = pd.DataFrame(wstethRates)
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
            description="Lido wstETH APR rates",
            table_name="wsteth_APR_rates", # define your table name here
            is_private=False
        )
else:
    print('Now is not the time')
