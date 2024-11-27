#gets daily snapshot update of the APRs of Alchemix's vaults

from graphKey import returnKey
import requests
import json
from twos_complement import twos_complement
from datetime import datetime
import pandas as pd
from pinata import pinataHash, pinataPin, pinataDelete, pinataPinFile
from aaveRate import getAaveAvgApr #(timestamp, address, network)

def getAaveApr (address, network):
# gets aave apr rate

    graphApiKey = returnKey()

    if network == 'mainnet':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N'

    if network == 'optimism':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/DSfLz8oQBUeU5atALgUFQKMTSYV9mZAVYp4noLSXAfvb'

    if network == 'arbitrum':
        graphURL = 'https://gateway-arbitrum.network.thegraph.com/api/' + graphApiKey + '/subgraphs/id/DLuE98kEb5pQNXAcKFQGQgfSQ57Xdou4jnVbAEqMfy3B'
    # url for querying the graph

    query = '''
        {
          reserveParamsHistoryItems(
            where: {reserve_: {aToken: "''' + address.lower() + '''"}}
            orderBy: timestamp
            orderDirection: desc
            first: 1
            skip: 0
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
    # query for aave apr for given token

    data = {
        "query" : query
    }
    # puts the query into a usable data thingy for making a web request

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    print('Making aave request')
    queryResponse = requests.post(graphURL, json=data, headers=headers)

    queryData = queryResponse.json()

    apr = int(queryData['data']['reserveParamsHistoryItems'][0]['liquidityRate']) / (10 ** 27)

    return apr

def getYearnApr (address, network):

    if network == 'mainnet':
        networkID = '1'

    if network == 'optimism':
        networkID = '10'

    if network == 'arbitrum':
        networkID = '42161'

    yearnURL = 'https://ydaemon.yearn.fi/' + networkID + '/vaults/' + address

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    print('Making yearn request')
    yearnData = requests.get(yearnURL, headers=headers)
    yearnData = yearnData.json()

    return yearnData['apr']['netAPR']

def getVesperApr (name):

    url = 'https://api.vesper.finance/pools'
    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    print('Making Vesper request')
    vesperInfo = requests.get(url, headers=headers)
    vesperInfo = vesperInfo.json()

    for token in vesperInfo:
        if token['name'] == name:
            apr = token['actualRates']['30']

    return float(apr) / 100

def getWstEthApr ():

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    url = 'https://eth-api.lido.fi/v1/protocol/steth/apr'

    print('Getting page count')
    firstPage = requests.get(url, headers=headers)
    firstPage = firstPage.json()

    pageCount = firstPage['pagination']['pageCount']

    lastURL = url + '?page=' + str(pageCount)

    print('Getting most recent apr')
    lastPage = requests.get(lastURL, headers=headers)
    lastPage = lastPage.json()

    apr = float(lastPage['data'][-1]['apr']) / 100

    return apr

def getRethApr ():

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    url = 'https://api.rocketpool.net/api/mainnet/apr'

    print('Making rETH request')
    rethInfo = requests.get(url, headers=headers)
    rethInfo = rethInfo.json()

    apr = float(rethInfo['yearlyAPR']) / 100

    return apr

def getSfrxEthApr ():

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    url = 'https://api.frax.finance/v2/frxeth/summary/latest'

    sfrxethInfo = requests.get(url, headers=headers)
    sfrxethInfo = sfrxethInfo.json()

    apr = float(sfrxethInfo['sfrxethApr']) / 100

    return apr

def getCustomApr (name):

    if name == 'wstETH':
        return getWstEthApr()
    elif name == 'rETH':
        return getRethApr()
    elif name == 'sfrxETH':
        return getSfrxEthApr()
    else:
        return 0

def getJusdcApr():

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    url = 'https://app.jonesdao.io/api/jusdc-apy'

    print('Making jUSDC request')
    jusdcInfo = requests.get(url, headers=headers)
    jusdcInfo = jusdcInfo.json()

    apr = float(jusdcInfo['jusdcApy']) / 100

    return apr

def getGearboxApr(address, network):

    headers = {
        "Content-Type": "application/json"
    }
    #api call request headers

    keyString = '/home/imimim/alchemix/user_debt/alchemy_api_key_mainnet.txt'

    apiKey = open(keyString, "r")
    # get the alchemy api key for network

    keyValue = apiKey.read()
    # read the key from the file

    apiKey.close()
    # close the opened file

    print(network)
    if network == 'mainnet':
        alchemyBase = 'https://eth-mainnet.g.alchemy.com/v2/'
    elif network == 'optimism':
        alchemyBase = 'https://opt-mainnet.g.alchemy.com/v2/'
    elif network == 'arbitrum':
        alchemyBase = 'https://arb-mainnet.g.alchemy.com/v2/'
    else:
        print('Oops. No bullets (network)')
        return 0

    apiString = alchemyBase + keyValue

    requestPayload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": address,
                "data": "0x72f702f3"
            },
            "latest"
        ]
    }

    print("Looking up gearbox staking token")

    apiPost = requests.post(apiString, headers=headers, data=json.dumps(requestPayload))
    apiPost = apiPost.json()

    stakingToken = '0x' + apiPost['result'][-40:]

    print('Staking token: ', stakingToken)

    requestPayload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": stakingToken,
                "data": "0xad2961a3"
            },
            "latest"
        ]
    }

    print('Looking up gearbox supply rate')

    apiPost = requests.post(apiString, headers=headers, data=json.dumps(requestPayload))
    apiPost = apiPost.json()

    print('Supply rate: ', apiPost['result'])
    apr = twos_complement(apiPost['result']) / 1e27

    return apr

def doMainnet (timestamp):
    mainnetVaults = [
        {
            'name' : 'yvDAI',
            'contract' : '0xda816459f1ab5631232fe5e97a05bbbb94970c95',
            'type' : 'yearn'
        },
        {
            'name' : 'yvUSDC',
            'contract' : '0xa354f35829ae975e850e23e9615b11da1b3dc4de',
            'type' : 'yearn'
        },
        {
            'name' : 'yvUSDT',
            'contract' : '0x3B27F92C0e212C671EA351827EDF93DB27cc0c65',
            'type' : 'yearn'
        },
        {
            'name' : 'aDAI',
            'contract' : '0x028171bCA77440897B824Ca71D1c56caC55b68A3',
            'type' : 'aave'
        },
        {
            'name' : 'aUSDC',
            'contract' : '0xBcca60bB61934080951369a648Fb03DF4F96263C',
            'type' : 'aave'
        },
        {
            'name' : 'aUSDT',
            'contract' : '0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811',
            'type' : 'aave'
        },
        {
            'name' : 'vaUSDC',
            'contract' : '0xa8b607aa09b6a2e306f93e74c282fb13f6a80452',
            'type' : 'vesper'
        },
        {
            'name' : 'vaDAI',
            'contract' : '0x0538C8bAc84E95A9dF8aC10Aad17DbE81b9E36ee',
            'type' : 'vesper'
        },
        {
            'name' : 'vaFRAX',
            'contract' : '0xc14900dFB1Aa54e7674e1eCf9ce02b3b35157ba5',
            'type' : 'vesper'
        },
        {
            'name' : 'aFRAX',
            'contract' : '0xd4937682df3C8aEF4FE912A96A74121C0829E664',
            'type' : 'aave'
        },
        {
            'name' : 'yvWETH',
            'contract' : '0xa258c4606ca8206d8aa700ce2143d7db854d168c',
            'type' : 'yearn'
        },
        {
            'name' : 'wstETH',
            'contract' : '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0',
            'type' : 'custom'
        },
        {
            'name' : 'rETH',
            'contract' : '0xae78736cd615f374d3085123a210448e74fc6393',
            'type' : 'custom'
        },
        {
            'name' : 'aWETH',
            'contract' : '0x030bA81f1c18d280636F32af80b9AAd02Cf0854e',
            'type' : 'aave'
        },
        {
            'name' : 'vaETH',
            'contract' : '0xd1c117319b3595fbc39b471ab1fd485629eb05f2',
            'type' : 'vesper'
        },
        {
            'name' : 'sfrxETH',
            'contract' : '0xac3E018457B222d93114458476f3E3416Abbe38F',
            'type' : 'custom'
        }
    ]

    mainnetRates = []

    print('MAINNET')
    print('-------')
    for token in mainnetVaults:

        if token['type'] == 'aave':
            print(token['name'])
            apr = getAaveAvgApr (timestamp, token['contract'], 'mainnet') #gets average apr from priot 24 hours
            if apr == 'empty':
                print('No rates from the last 24 hours. getting most recent one instead.')
                apr = getAaveApr(token['contract'], 'mainnet') #if no rates from the prior 24 hours, it just gets the most recent one instead
            print('APR')
            print(apr)

        if token['type'] == 'yearn':
            print(token['name'])
            apr = getYearnApr (token['contract'], 'mainnet')
            print('APR')
            print(apr)

        if token['type'] == 'vesper':
            print(token['name'])
            apr = getVesperApr (token['name'])
            print('APR')
            print(apr)

        if token['type'] == 'custom':
            print(token['name'])
            apr = getCustomApr (token['name'])
            print('APR')
            print(apr)

        tokenRate = {
            'timestamp' : timestamp,
            'name' : token['name'],
            'apr' : apr
        }

        mainnetRates.append(tokenRate)

    return mainnetRates

def doOptimism(timestamp):

    optimismVaults = [
        {
            'name' : 'aDAI',
            'contract' : '0x82E64f49Ed5EC1bC6e43DAD4FC8Af9bb3A2312EE',
            'type' : 'aave'
        },
        {
            'name' : 'aUSDC',
            'contract' : '0x625E7708f30cA75bfd92586e17077590C60eb4cD',
            'type' : 'aave'
        },
        {
            'name' : 'aUSDT',
            'contract' : '0x6ab707Aca953eDAeFBc4fD23bA73294241490620',
            'type' : 'aave'
        },
        {
            'name' : 'yvUSDC',
            'contract' : '0xaD17A225074191d5c8a37B50FdA1AE278a2EE6A2',
            'type' : 'yearn'
        },
        {
            'name' : 'yvDAI',
            'contract' : '0x65343F414FFD6c97b0f6add33d16F6845Ac22BAc',
            'type' : 'yearn'
        },
        {
            'name' : 'aWETH',
            'contract' : '0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8',
            'type' : 'aave'
        },
        {
            'name' : 'wstETH',
            'contract' : '0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb',
            'type' : 'custom'
        },
        {
            'name' : 'yvWETH',
            'contract' : '0x5B977577Eb8a480f63e11FC615D6753adB8652Ae',
            'type' : 'yearn'
        }
    ]

    optimismRates = []

    print('OPTIMISM')
    print('---------')
    for token in optimismVaults:

        if token['type'] == 'aave':
            print(token['name'])
            #apr = getAaveApr(token['contract'], 'optimism')
            apr = getAaveAvgApr (timestamp, token['contract'], 'optimism') #gets average apr from priot 24 hours
            if apr == 'empty':
                print('No rates from the last 24 hours. getting most recent one instead.')
                apr = getAaveApr(token['contract'], 'optimism') #if no rates from the prior 24 hours, it just gets the most recent one instead
            print('APR')
            print(apr)

        if token['type'] == 'yearn':
            print(token['name'])
            apr = getYearnApr (token['contract'], 'optimism')
            print('APR')
            print(apr)

        if token['type'] == 'vesper':
            print(token['name'])
            apr = getVesperApr (token['name'])
            print('APR')
            print(apr)

        if token['type'] == 'custom':
            print(token['name'])
            apr = getCustomApr (token['name'])
            print('APR')
            print(apr)

        tokenRate = {
            'timestamp' : timestamp,
            'name' : token['name'],
            'apr' : apr
        }

        optimismRates.append(tokenRate)

    return optimismRates


def doArbitrum(timestamp):

    arbitrumVaults = [
        {
            'name' : 'aUSDC',
            'contract' : '0x724dc807b04555b71ed48a6896b6F41593b8C637',
            'type' : 'aave'
        },
        {
            'name' : 'jUSDC',
            'contract' : '0xb0bde111812eac913b392d80d51966ec977be3a2',
            'type' : 'jones'
        },
        {
            'name' : 'wstETH',
            'contract' : '0x5979D7b546E38E414F7E9822514be443A4800529',
            'type' : 'custom'
        },
        {
            'name' : 'farmdWETHV3',
            'contract' : '0xf3b7994e4dA53E04155057Fd61dc501599d57877',
            'type' : 'gearbox'
        }
    ]

    arbitrumRates = []

    print('ARBITRUM')
    print('---------')
    for token in arbitrumVaults:

        if token['type'] == 'aave':
            print(token['name'])
            #apr = getAaveApr(token['contract'], 'arbitrum')
            apr = getAaveAvgApr (timestamp, token['contract'], 'arbitrum') #gets average apr from priot 24 hours
            if apr == 'empty':
                print('No rates from the last 24 hours. getting most recent one instead.')
                apr = getAaveApr(token['contract'], 'arbitrum') #if no rates from the prior 24 hours, it just gets the most recent one instead
            print('APR')
            print(apr)

        if token['type'] == 'yearn':
            print(token['name'])
            apr = getYearnApr (token['contract'], 'arbitrum')
            print('APR')
            print(apr)

        if token['type'] == 'vesper':
            print(token['name'])
            apr = getVesperApr (token['name'])
            print('APR')
            print(apr)

        if token['type'] == 'custom':
            print(token['name'])
            apr = getCustomApr (token['name'])
            print('APR')
            print(apr)

        if token['name'] == 'jUSDC':
            print(token['name'])
            apr = getJusdcApr()
            print('APR')
            print(apr)

        if token['type'] == 'gearbox':
            print(token['name'])
            apr = getGearboxApr(token['contract'], 'arbitrum')
            print('APR')
            print(apr)

        tokenRate = {
            'timestamp' : timestamp,
            'name' : token['name'],
            'apr' : apr
        }

        arbitrumRates.append(tokenRate)

    return arbitrumRates

checkTime = int(datetime.utcnow().timestamp())

mainnetFile = 'mainnetDailyAprs.csv'
optimismFile = 'optimismDailyAprs.csv'
arbitrumFile = 'arbitrumDailyAprs.csv'

mainnetCsvPath = '/home/imimim/alchemix/APRs/' + mainnetFile
optimismCsvPath = '/home/imimim/alchemix/APRs/' + optimismFile
arbitrumCsvPath = '/home/imimim/alchemix/APRs/' + arbitrumFile

dailyAPRs = {
    'mainnetRates' : doMainnet(checkTime),
    'optimismRates' : doOptimism(checkTime),
    'arbitrumRates' : doArbitrum(checkTime)
}

print(dailyAPRs)


print('Writing CSVs')
df = pd.DataFrame(dailyAPRs['mainnetRates'])
df.to_csv(mainnetCsvPath, mode='a', index=False, header=False)

df = pd.DataFrame(dailyAPRs['optimismRates'])
df.to_csv(optimismCsvPath, mode='a', index=False, header=False)

df = pd.DataFrame(dailyAPRs['arbitrumRates'])
df.to_csv(arbitrumCsvPath, mode='a', index=False, header=False)


hash = pinataHash(mainnetFile)
print('Old mainnet hash: ', hash)
print('Deleting old hash')
pinataDelete(hash)
#pin new file to pinata
pinataPinFile(mainnetCsvPath, mainnetFile, 'r') #filetype: 'r' for textfile 'rb' for binary

hash = pinataHash(optimismFile)
print('Old optimism hash: ', hash)
print('Deleting old hash')
pinataDelete(hash)
#pin new file to pinata
pinataPinFile(optimismCsvPath, optimismFile, 'r') #filetype: 'r' for textfile 'rb' for binary

hash = pinataHash(arbitrumFile)
print('Old arbitrum hash: ', hash)
print('Deleting old hash')
pinataDelete(hash)
#pin new file to pinata
pinataPinFile(arbitrumCsvPath, arbitrumFile, 'r') #filetype: 'r' for textfile 'rb' for binary
