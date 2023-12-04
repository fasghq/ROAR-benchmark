from os import listdir
from os.path import isfile, join
import json
import pandas as pd
from tqdm import tqdm

quicknodePath = '/home/ubuntu/projects/unipro/models/rarity/metadata_quicknode/' 
alchemyPath = '/home/ubuntu/projects/unipro/models/rarity/metadata_alchemy/'
covalentPath = '/home/ubuntu/projects/unipro/models/rarity/metadata_covalent/'

onlyfiles = [f for f in listdir(quicknodePath) if isfile(join(quicknodePath, f))]

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()
contractSupplies = collectionsDF['Total Supply'].tolist()

contractNames = ['CG']
contractAddresses = ['0x0322F6f11A94CFB1b5B6E95E059d8DEB2bf17D6A']
contractSupplies = [6969]

#all_ids = [i for i in range(1, contractSupplies[0] + 1)]

fix_with = None

missingCollections = {}
for i in tqdm(range(len(contractNames))):
    with open(quicknodePath + contractNames[i] + '_metadata.json', 'r') as file:
        data = json.load(file)
        missingCollections[contractNames[i]] = []

        if len(data) != int(contractSupplies[i]):
            print(f"{contractNames[i]} wrong token number: {len(data)} < {int(contractSupplies[i])}")

        if fix_with != 'moonbird':
            for token in tqdm(data):
                #all_ids.remove(int(token['collectionTokenId']))
                if len(token['traits']) == 0:
                    if fix_with == 'covalent':
                        with open(covalentPath + contractNames[i] + '_metadata.json', 'r') as file:
                            data_covalent = json.load(file)
                            for token_covalent in data_covalent:
                                if token_covalent['nft_data']['token_id'] == token['collectionTokenId']:
                                    token['traits'] = token_covalent['nft_data']['external_data']['attributes']
                    elif fix_with == 'alchemy':
                        with open(alchemyPath + contractNames[i] + '_metadata.json', 'r') as file:
                            data_alchemy = json.load(file)
                            for token_alchemy in data_alchemy:
                                if token_alchemy['tokenId'] == token['collectionTokenId']:
                                    token['traits'] = token_alchemy['raw']['metadata']['attributes']
                    elif fix_with is None:
                        missingCollections[contractNames[i]].append(token['collectionTokenId'])
        elif fix_with == 'moonbird':
            with open(covalentPath + contractNames[i] + '_metadata.json', 'r') as file:
                data_covalent = json.load(file)
                for token_covalent in tqdm(data_covalent):
                    if token_covalent['nft_data']['token_id'] != "1":
                        new_token = {
                            "collectionName": "Moonbirds",
                            "collectionAddress": "0x23581767a106ae21c074b2276d25e5c3e136a68b",
                            "collectionTokenId": token_covalent['nft_data']['token_id'],
                            "description": "",
                            "name": "#" + token_covalent['nft_data']['token_id'],
                            "imageUrl": f"https://live---metadata-5covpqijaa-uc.a.run.app/images/{token_covalent['nft_data']['token_id']}",
                            "traits": token_covalent['nft_data']['external_data']['attributes'],
                            "chain": "ETH",
                            "network": "MAINNET"
                        }
                        data.append(new_token)            
    
    if fix_with is not None:
        with open(quicknodePath + contractNames[i] + '_metadata.json', 'w') as file:
            json.dump(data, file, indent=2)

#print(all_ids)

if fix_with is None:
    with open('/home/ubuntu/projects/unipro/models/rarity/missings_quicknode_new.json', 'w') as file:
        json.dump(missingCollections, file, indent=2)
