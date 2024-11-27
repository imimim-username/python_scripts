def pinataHash (pinata_file_name):
# looks up a file hash in pinata based on the file name
    import requests
    import json

    api_key = open("/home/imimim/alchemix/dune/pinata_api_key.txt", "r")
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
    import requests
    import json

    api_key = open("/home/imimim/alchemix/dune/pinata_api_key.txt", "r")
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

    print("Pinning ", pinata_file_name, " to pinata")
    pinata_post = requests.post(pinata_json_url, headers = request_headers, data=json.dumps(request_data))
    # calls the pinata API for writing values to pinata

    result = pinata_post.json()
    # turns the result into a usable json

    print("Pinata post result")
    print(result)

def pinataDelete (fileHash):
# unpins a file on pinata based on its hash
    import requests
    import json

    api_key = open("/home/imimim/alchemix/dune/pinata_api_key.txt", "r")
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
    # unpin old file in pinata
    print(unpin.text)

def pinataPinFile (filePath, fileName, fileType):
# pins a non-json file to pinata
# filetype: 'r' for textfile 'rb' for binary

    import requests
    import json

    api_key = open("/home/imimim/alchemix/arbitrum/pinata_api_key.txt", "r")
    # get the pinata_api_key

    pinata_key = api_key.read()
    # read the key from the file

    api_key.close()
    # close the opened file

    request_headers = {
        "Authorization": pinata_key
    }

    pinURL = 'https://api.pinata.cloud/pinning/pinFileToIPFS'

    # Read file
    with open(filePath, fileType) as file:
        files = {'file': file}

        # Construct metadata
        pinataMetadata = {
            "name": fileName
        }

        # Construct pinataOptions
        pinataOptions = {
            "cidVersion": 0
        }

        # Construct headers
        headers = request_headers

        # Construct payload
        payload = {
            "pinataMetadata": json.dumps(pinataMetadata),
            "pinataOptions": json.dumps(pinataOptions)
        }

        print('Pinning ', fileName)
        # POST request
        response = requests.post(pinURL,
                                 headers=headers,
                                 files=files,
                                 data=payload)

        # Handle response
        resData = response.json()
        print(resData)

