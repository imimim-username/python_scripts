def getAaveAvgApr (timestamp, address, network):
# gets average Apr of the prior 24 hours of a given aave token from the prior 24 hours

    import requests
    from graphKey import returnKey
    #import json
    #from twos_complement import twos_complement
    #from datetime import datetime
    #import pandas as pd

    graphApiKey = returnKey()

    if network == 'mainnet':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N'

    if network == 'optimism':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/DSfLz8oQBUeU5atALgUFQKMTSYV9mZAVYp4noLSXAfvb'

    if network == 'arbitrum':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/DLuE98kEb5pQNXAcKFQGQgfSQ57Xdou4jnVbAEqMfy3B'
    # url for querying the graph

    startTime = timestamp - 86400

    query = '''
    {
        reserveParamsHistoryItems(
            where: {reserve_: {aToken: "''' + address.lower() + '''"}, timestamp_gte: ''' + str(startTime) + ''', timestamp_lte: ''' + str(timestamp) + '''}
            orderBy: timestamp
            orderDirection: desc
            first: 1000
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
    '''
    # query for getting aave aprs from a given time range

    data = {
        "query" : query
    }
    # puts the query into a usable data thingy for making a web request

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    print('Making Aave graph request')
    queryResponse = requests.post(graphURL, json=data, headers=headers)

    queryResponse = queryResponse.json()

    # print(queryResponse)

    numItems = len(queryResponse['data']['reserveParamsHistoryItems'])
    print('Number of items: ', numItems)

    if numItems > 0:
        ratesTotal = 0
        # running total of the rates for the purpose of getting an average rate

        for item in queryResponse['data']['reserveParamsHistoryItems']:
            #print(item)
            rate = int(item['liquidityRate']) / (10 ** 27)
            print('Rate: ', rate)

            ratesTotal += rate
            #adds the rate to the ratesTotal for the purpose of getting an average

        ratesAverage = ratesTotal / numItems
        # average rate for the given time interval
    else: ratesAverage = 'empty'

    return ratesAverage

#thing = getAaveAvgApr (1732733814, '0x030ba81f1c18d280636f32af80b9aad02cf0854e', 'mainnet')

#print('Average rate: ', thing)