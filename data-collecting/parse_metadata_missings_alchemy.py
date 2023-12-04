from os import listdir
from os.path import isfile, join
import json
import pandas as pd
from tqdm import tqdm


alchemyPath = '/home/ubuntu/projects/unipro/models/rarity/metadata_alchemy/' 

onlyfiles = [f for f in listdir(alchemyPath) if isfile(join(alchemyPath, f))]

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()
contractSupplies = collectionsDF['Total Supply'].tolist()

contractNames = ['KILLABEARS']
contractAddresses = ['0xc99c679c50033bbc5321eb88752e89a93e9e83c5']
contractSupplies = [3333]

all_ids = [i for i in range(1, contractSupplies[0] + 1)]
missingCollections = {}

for i in tqdm(range(len(contractNames))):
    with open(alchemyPath + contractNames[i] + '_metadata.json', 'r') as file:
        data_alchemy = json.load(file)
        missingCollections[contractNames[i]] = []

        if len(data_alchemy) != int(contractSupplies[i]):
            print(f"{contractNames[i]} wrong token number: {len(data_alchemy)} < {int(contractSupplies[i])}")

        for token in tqdm(data_alchemy):
            all_ids.remove(int(token['tokenId']))
            if len(token['raw']['metadata']) == 0:
                missingCollections[contractNames[i]].append(token['tokenId'])
            elif len(token['raw']['metadata']['attributes']) == 0:
                missingCollections[contractNames[i]].append(token['tokenId'])

print(all_ids)

with open('/home/ubuntu/projects/unipro/models/rarity/missings_alchemy_add.json', 'w') as file:
    json.dump(missingCollections, file, indent=2)


