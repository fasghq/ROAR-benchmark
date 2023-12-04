import requests
import json
import pandas as pd
from tqdm import tqdm

headers = {"accept": "application/json"}
key = 'xkks-g1YtxL9-kRoJAGR0_CqsiVcobLR'

alchemyPath = '/home/ubuntu/projects/unipro/models/rarity/metadata_alchemy/'

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()

contractNames = ['KARMA', 'KILLABEARS']
contractAddresses = ['0x86cc280d0bac0bd4ea38ba7d31e895aa20cceb4b', '0xc99c679c50033bbc5321eb88752e89a93e9e83c5']

def do_md_request(contractAddress, contractName):
    pageKey = ''
    metadata = []
    initial = True
    
    while True:
        if initial:
            url = ("https://eth-mainnet.g.alchemy.com/nft/v3/" + key + 
                "/getNFTsForContract?contractAddress=" + contractAddress +
                "&withMetadata=true&limit=100"
            )
        else:
            url = ("https://eth-mainnet.g.alchemy.com/nft/v3/" + key + 
                "/getNFTsForContract?contractAddress=" + contractAddress +
                "&withMetadata=true&limit=100&startToken=" + str(startToken)
            )
            
        response = requests.get(url, headers=headers).text
        
        try:
            nftMetadata = json.loads(response)
            metadata += nftMetadata['nfts']
            pageKey = nftMetadata['pageKey']
        except:
            print(response)
            break      
        
        with open(alchemyPath + contractName + '_metadata.json', "w") as file:
            json.dump(metadata, file, indent=2) 

        if pageKey is None:
            break
        else:
            startToken = int(metadata[-1]['tokenId']) + 1
            initial = False

for i in tqdm(range(len(contractAddresses))):
    print(contractNames[i] + ' started parsing.')
    do_md_request(contractAddresses[i], contractNames[i])
    print(contractNames[i] + ' finished parsing.')