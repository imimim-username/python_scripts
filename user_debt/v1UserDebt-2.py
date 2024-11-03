#gets how much debt remains in v1 system

import datetime
# to check for day of the week

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

def hasMigrated (address):
# evaluates whether an address has migrated to v2 already
# one for DAI, and one for ETH
# Because apparently the v1 alchemist does not update debt values after migration
# So a user that has migrated will need to have their debt manually set to 0.

    api_key = open("/home/imimim/alchemix/user_debt/alchemy_api_key_mainnet.txt", "r")
    # get the alchemy_api_key

    alchemy_key = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    apiString = "https://eth-mainnet.g.alchemy.com/v2/" + alchemy_key
    # constructs the alchemy api key

    migrationStatus = {
        "alUSD" : "0",
        "alETH" : "0"
    }

    # instantiates return data

    request_headers = {
        "Content-Type": "application/json"
    }
    # alchemy api call request headers

    print("Checking to see if address has migrated")

    alusdAdapter = "0x0bb35D6CeE977c7c9C6B8ccAc8b547a38ee4A666"
    alethAdapter = "0xEdac7076B8928a2eA3c9421BB859105cCe35ADFd"
    # Adapter contract addresses

    dataString = "0xd7625c88000000000000000000000000" + address[2:42]

    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params" : [
            {
                "from": "0x0000000000000000000000000000000000000000",
                "data": dataString,
                "to": alusdAdapter
            },
            "latest"
        ],
    }
    # api request payload for alusd alchemist migration status

    api_post = requests.post(apiString, headers=request_headers, data=json.dumps(request_data))
    # calls the alchemy mainnet API for alusd migration status using the above settings

    result = api_post.json()
    # turns the result into a usable json

    alusdMigStatus = result["result"][-1]
    print("alUSD migration status: ")
    print(alusdMigStatus)
    migrationStatus["alUSD"] = alusdMigStatus
    # sets the alusd migration status to the last character of the result. 1 is true, 0 is false.

    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params" : [
            {
                "from": "0x0000000000000000000000000000000000000000",
                "data": dataString,
                "to": alethAdapter
            },
            "latest"
        ],
    }
    # api request payload for alusd alchemist migration status

    api_post = requests.post(apiString, headers=request_headers, data=json.dumps(request_data))
    # calls the alchemy mainnet API for aleth migration status using the above settings

    result = api_post.json()
    # turns the result into a usable json

    alethMigStatus = result["result"][-1]
    print("alETH migration status: ")
    print(alethMigStatus)
    migrationStatus["alETH"] = alethMigStatus
    # sets the alETH migration status to the last character of the result. 1 is true, 0 is false.

    return migrationStatus


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
        data_string = "0xaa6e0434000000000000000000000000" + x["address"][2:42]
        # the data string that goes into the payload, which includes the contract method id and the user address
        # "0xaa6e0434000000000000000000000000a22b175600d70db5388b9de2c47dc8c0b2f06aa7"

        print("Address: ")
        print(addressData[y])

        migrationStatus = hasMigrated(addressData[y]["address"])
        # gets migration status of address

        if migrationStatus["alUSD"] == "1":
        # if address has migrated alUSD, then alusd debt is set to 0
            addressData[y]["alusd_debt"] = 0
        else:
        # if address has not migrated, then calculates alUSD debt
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

        if migrationStatus["alETH"] == "1":
        # if address has migrated alETH, the aleth debt is set to 0
            addressData[y]["aleth_debt"] = 0
        else:
        # if address has not migrated, then calculates alETH debt
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
    # file that contains list of optimism addresses that have deposited into alchemists

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

today = datetime.date.today()
weekday = today.weekday()
# for determining day of week

if (weekday == 0):
    deployments = {
        "deployment" : [
            {
                "network" : "mainnet",
                "alchemy_api_string" : "https://eth-mainnet.g.alchemy.com/v2/",
                "api_key" : "/home/imimim/alchemix/user_debt/alchemy_api_key_mainnet.txt",
                "address_list" : "v1DebtAddresses.json",
                "data_file" : "v1UserDebt.json",
                "alUSD" : "0xc21D353FF4ee73C572425697f4F5aaD2109fe35b",
                "alETH" : "0xf8317BD5F48B6fE608a52B48C856D3367540B73B"
            }
        ]
    }

    for z in deployments["deployment"]:
        print (z)
        doTheThing(z)

    # print('Running make.com update')
    #makeWebhook = 'https://hook.us1.make.com/[webhookinfo]'
    #updateMake = requests.get(makeWebhook)
    # calls the make webhook to update the Pinata locations json file
    # makeStatus = updateMake.status_code
    # print ('make.com status code :', makeStatus)

else:
    print("Today is not the correct day of the week")

end = time.time()
# stop the timer

duration = end - start

print("This thing took")
print(duration)
print("seconds to execute")
