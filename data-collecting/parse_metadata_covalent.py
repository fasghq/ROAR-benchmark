import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
from tqdm import tqdm

headers_md = {
    "accept": "application/json",
}
basic = HTTPBasicAuth('cqt_rQPyMwcM6CRBGJjDbXwJxhXtbhGY', '')

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()

metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata/'

def do_md_request(contractAddress, contractName):
    pageKey = ''
    metadata = []
    initial = True
    
    while True:
        if initial:
            url = ('https://api.covalenthq.com/v1/eth-mainnet/nft/' + contractAddress +
                   '/metadata/')
        else:
            url = ('https://api.covalenthq.com/v1/eth-mainnet/nft/' + contractAddress +
                   '/metadata/' + '?page-number=' + str(pagination['page_number'] + 1))
            
        response = requests.get(url, headers=headers_md, auth=basic).text
        
        try:
            nftMetadata = json.loads(response)['data']
            metadata += nftMetadata['items']
            pagination = nftMetadata['pagination']
            #print(pagination)
            #print(len(metadata))
        except:
            print(response)
            break      
        
        with open(metadataPath + contractName + '_metadata.json', "w") as file:
            json.dump(metadata, file, indent=2) 
        
        if pagination['total_count'] > 50000:
            print('Collection', contractName, 'is too big:', pagination['total_count'])
            return False
        
        if pagination['has_more']:
            initial = False
        else:
            break

contractAddresses = ['0x86cc280d0bac0bd4ea38ba7d31e895aa20cceb4b', '0xc99c679c50033bbc5321eb88752e89a93e9e83c5']
contractNames = ['KARMA', 'KILLABEARS']

for i in tqdm(range(len(contractAddresses))):
    do_md_request(contractAddresses[i], contractNames[i])
    print(contractNames[i] + ' finished parsing.')