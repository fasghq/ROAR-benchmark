from os import listdir
from os.path import isfile, join
import json
import requests
import pandas as pd

metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata/'

onlyfiles = [f for f in listdir(metadataPath) if isfile(join(metadataPath, f))]

missingCollections = {}
for fileName in onlyfiles:
    with open(metadataPath + fileName, 'r') as file:
        data = json.load(file)
        # print(fileName[:fileName.find("_")])
        missingCollections[fileName[:fileName.find("_")]] = []

        for token in data:
            try:
                if len(token['nft_data']['external_data']) == 0:
                    #print(fileName[:fileName.find("_")], token['nft_data']['token_id'])
                    missingCollections[fileName[:fileName.find("_")]].append(token['nft_data']['token_id'])
                elif len(token['nft_data']['external_data']['attributes']) == 0:
                    #print(fileName[:fileName.find("_")], token['nft_data']['token_id'])
                    #print(token['nft_data']['token_id'])
                    missingCollections[fileName[:fileName.find("_")]].append(token['nft_data']['token_id'])
            except:
                print(fileName[:fileName.find("_")], token['nft_data']['token_id'])
                missingCollections[fileName[:fileName.find("_")]].append(token['nft_data']['token_id'])
                #print(token)
                #print(token['nft_data']['token_id'])
    with open(metadataPath + fileName, 'w') as file:
        json.dump(data, file, indent=2)

with open('/home/ubuntu/projects/unipro/models/rarity/missings_covalent.json', 'w') as file:
    json.dump(missingCollections, file, indent=2)