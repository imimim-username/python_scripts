#user debt in v2 system
import requests
# to make web requests

import json
# for doing json things

import time
# just to measure how long this thing takes to execute

def twos_complement(hex_value):
# converts hex number to decimal, including negative hex numbers

    decimal_value = int(hex_value, 16)
    bit_length = len(hex_value) * 4
    if decimal_value & (1 << (bit_length - 1)):
        decimal_value -= 1 << bit_length
    return decimal_value

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


def getDebt (addressData, apiCall, alUSDalchemist, alETHalchemist):
# gets debts of addresses using the relevant apiCall (different networks have a different API endpoint) and relevant alchemist address

    request_headers = {
        "Content-Type": "application/json"
    }
    # alchemy api call request headers

    print("Gathering network debt values")

    y = 0
    # counter

    for x in addressData:
    # iterate through all the addresses in the list
        data_string = "0x5e5c06e2000000000000000000000000" + x["address"][2:42]
        # the data string that goes into the payload, which includes the contract method id and the user address

        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params" : [
                {
                    "from": "0x0000000000000000000000000000000000000000",
                    "data": data_string,
                    "to": alUSDalchemist
                },
                "latest"
            ],
        }
        # api request payload for alusd debt value

        api_post = requests.post(apiCall, headers=request_headers, data=json.dumps(request_data))
        # calls the alchemy mainnet API for alusd debt using the above settings

        result = api_post.json()
        # turns the result into a usable json

        hex_val = result["result"][2:66]
        # from the result, extracts the hex value that contains the user debt value

        decimal = twos_complement(hex_val)
        # converts the debt value from hex to decimal

        decimal = decimal / (10 ** 18)
        # converts decimal to human readable format

        addressData[y]["alusd_debt"]=decimal
        # adds alusd debt value to the address

        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params" : [
                {
                    "from": "0x0000000000000000000000000000000000000000",
                    "data": data_string,
                    "to": alETHalchemist
                },
                "latest"
            ],
        }
        # api request payload for aleth debt value

        api_post = requests.post(apiCall, headers=request_headers, data=json.dumps(request_data))
        # calls the alchemy mainnet API for aleth debt using the above settings

        result = api_post.json()
        # turns the result into a usable json

        hex_val = result["result"][2:66]
        # from the result, extracts the hex value that contains the user debt value

        decimal = twos_complement(hex_val)
        # converts the debt value from hex to decimal

        decimal = decimal / (10 ** 18)
        # converts decimal to human readable format

        addressData[y]["aleth_debt"]=decimal
        # adds the alETH debt value to the addresss

        print(addressData[y])
        y = y + 1
        # iterate counter

        # if y == 5:
        #    return addressData
        # keeping it short to do testing

    return addressData

def doTheThing (dataIn):
# gets list of addresses, unpins old debt file, pins new debt file

    addressList = dataIn["address_list"]
    # file name that contains list of addresses that have deposited on the network

    print("Downloading " + dataIn["network"] + " address list")
    pinataURL = "https://ipfs.imimim.info/ipfs/" + pinataHash(addressList)
    # file that contains list of addresses that have deposited into alchemists

    requestAddress = requests.get(url = pinataURL)
    # requesting the list of addresses that have deposited into alchemists

    addressData = requestAddress.json()
    # converts addresses to json format

    api_key = open(dataIn["api_key"], "r")
    # get the alchemy api key for network

    keyValue = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    api_string = dataIn["alchemy_api_string"]
    # alchemy api endpoint

    api_call = api_string + keyValue
    # contstruct the full URL for calling alchemy API

    alUSD = dataIn["alUSD"]
    alETH = dataIn["alETH"]
    # alchemist addresses

    debts = getDebt (addressData, api_call, alUSD, alETH)

    file_name = dataIn["data_file"]
    # the file name that is used for storing and searching for user debt on pinata

    print("Looking up old user debt file on pinata")
    pinata_file_location = pinataHash(file_name)
    # looking for pre-existing file on pinata

    pinataDelete(pinata_file_location)
    # unpin old optimism debt json on pinata

    pinataPin (file_name, debts)
    # pin the debt data as json file in pinata

start = time.time()
# starting the timeer to measure how long execution takes
print("Starting timer")

deployments = {
    "deployment" : [
        {
            "network" : "mainnet",
            "alchemy_api_string" : "https://eth-mainnet.g.alchemy.com/v2/",
            "api_key" : "/home/imimim/alchemix/user_debt/alchemy_api_key_mainnet.txt",
            "address_list" : "mainnet_user_debt_addresses.json",
            "data_file" : "mainnet_user_debt.json",
            "alUSD" : "0x5c6374a2ac4ebc38dea0fc1f8716e5ea1add94dd", # alchemist address
            "alETH" : "0x062bf725dc4cdf947aa79ca2aaccd4f385b13b5c"  # alchemist address
        },
        {
            "network" : "optimism",
            "alchemy_api_string" : "https://opt-mainnet.g.alchemy.com/v2/",
            "api_key" : "/home/imimim/alchemix/user_debt/alchemy_api_key_optimism.txt",
            "address_list" : "optimism_user_debt_addresses.json",
            "data_file" : "optimism_user_debt.json",
            "alUSD" : "0x10294d57A419C8eb78C648372c5bAA27fD1484af", # alchemist address
            "alETH" : "0xe04Bb5B4de60FA2fBa69a93adE13A8B3B569d5B4"  # alchemist address
        },
        {
            "network" : "arbitrum",
            "alchemy_api_string" : "https://arb-mainnet.g.alchemy.com/v2/",
            "api_key" : "/home/imimim/alchemix/user_debt/alchemy_api_key_arbitrum.txt",
            "address_list" : "arbitrum_user_debt_addresses.json",
            "data_file" : "arbitrum_user_debt.json",
            "alUSD" : "0xb46eE2E4165F629b4aBCE04B7Eb4237f951AC66F", # alchemist address
            "alETH" : "0x654e16a0b161b150F5d1C8a5ba6E7A7B7760703A"  # alchemist address
        }
    ]
}

for z in deployments["deployment"]:
    print (z)
    # if z['network'] == 'arbitrum':
    #    doTheThing(z)
    doTheThing(z)

#print('Running make.com update')
#makeWebhook = 'https://hook.us1.make.com/[insert webhook]'
#updateMake = requests.get(makeWebhook)
# calls the make webhook to update the Pinata locations json file
#makeStatus = updateMake.status_code
#print ('make.com status code :', makeStatus)

end = time.time()
# stop the timer

duration = end - start

print("This thing took")
print(duration)
print("seconds to execute")
