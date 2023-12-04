import requests
import json
import pandas as pd
from tqdm import tqdm

url = "https://multi-twilight-morning.quiknode.pro/6ece7977d07e260834aac2831bd06a6f4d67caae/"

quicknodePath = '/home/ubuntu/projects/unipro/models/rarity/metadata_quicknode/'

headers = {
  'Content-Type': 'application/json'
}

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()

contractNames = ['XBORG']
contractAddresses = ['0xb452ff31b35dee74f2fdfd5194b91af1bad07b91']

def do_md_request(contractAddress, contractName):
    page = 1
    metadata = []
    
    while True:
        payload = json.dumps({
            "id": 67,
            "jsonrpc": "2.0",
            "method": "qn_fetchNFTsByCollection",
            "params": [{
                "collection": contractAddress,
                "page": page,
                "perPage": 100
            }]
        })
        
        response = requests.request("POST", url, headers=headers, data=payload).text
        try: 
            nftMetadata = json.loads(response)
            metadata += nftMetadata['result']['tokens']

        except:
            print(response)
            break      
        
        with open(quicknodePath + contractName + '_metadata.json', "w") as file:
            json.dump(metadata, file, indent=2) 

        if nftMetadata['result']['pageNumber'] < nftMetadata['result']['totalPages']:
            page = nftMetadata['result']['pageNumber'] + 1
        else:
            break



for i in tqdm(range(len(contractAddresses))):
    print(contractNames[i] + ' started parsing.')
    do_md_request(contractAddresses[i], contractNames[i])
    print(contractNames[i] + ' finished parsing.')