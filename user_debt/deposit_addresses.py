def uniqueDepositAddresses ():
    import requests
    import json

    from graphKey import returnKey

    import pandas as pd

    def getAddressInfo(endpoint, startingTime):

        query ='''
            {
              alchemistDepositEvents(
                orderBy: timestamp
                orderDirection: asc
                skip: 0
                first: 1000
                where: {timestamp_gte: "''' + str(startingTime) + '''"}
              ) {
                recipient
                timestamp
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
        response = requests.post(endpoint, json=queryPayload, headers=headers)

        responseInfo = response.json()

        #print(responseInfo)

        responseInfo = responseInfo['data']

        responseInfo = responseInfo['alchemistDepositEvents']

        #print(responseInfo)

        return(responseInfo)

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

    for deployment in deployments:

        toContinue = 0
        csvPath = '/home/imimim/alchemix/user_debt/' + deployment['network'] + '_addresses.csv'

        while toContinue == 0:

            print('Loading csv')
            dfLoad = pd.read_csv(csvPath)

            maxTimestamp = dfLoad['timestamp'].max()

            print('Last timestamp for ', deployment['network'])
            print(maxTimestamp)
            addressThing = getAddressInfo(deployment['graphEndpoint'], maxTimestamp)


            df = pd.DataFrame(addressThing)

            print('Appending to CSV')
            df.to_csv(csvPath, mode='a', header=False, index=False)

            print('number of entries')
            print(len(addressThing))

            toContinue = len(addressThing) % 1000

        dfFinal = pd.read_csv(csvPath)

        print('Dropping duplicates')
        dfFinal = dfFinal.drop_duplicates(subset=['recipient'])
        print('Dropping timestamps')
        dfFinal = dfFinal.drop(columns=['timestamp'])

        uniqueCsvPath = '/home/imimim/alchemix/user_debt/unique_' + deployment['network'] + '_addresses.csv'

        print('Writing unique addresses to csv')
        dfFinal.to_csv(uniqueCsvPath, index=False)





