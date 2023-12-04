import requests
import json
import pandas as pd
from tqdm import tqdm
import asyncio
import aiohttp

headers = {
    "accept": "application/json",
    "X-API-Key": "RGClA8BAbG2QX4vqqVyDtZAFfYaiTtGQ8Ma2PA8FoEUyPkBX"
}

metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata_mnemonic/'

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()
contractSupplies = collectionsDF['Total Supply'].tolist()

contractNames = ['HM']
contractAddresses = ['0xC2C747E0F7004F9E8817Db2ca4997657a7746928']
contractSupplies = [16384]

tokens_list = [
    "4216",
    "188",
    "2807",
    "3600",
    "4312",
    "6008",
    "6669",
    "7235",
    "7902",
    "9288",
    "10241",
    "11319",
    "11894",
    "14354",
    "1988",
    "4215",
    "6120",
    "7646",
    "10156",
    "11801",
    "125",
    "5132",
    "8672",
    "13763",
    "6725",
    "2957",
    "10747"
]

metadata = []

def do_md_request(contractAddress, contractName, contractSupply):
    for tokenId in tokens_list: #range(1, contractSupply + 1):
        url = f"https://ethereum-rest.api.mnemonichq.com/foundational/v1beta2/nfts/{contractAddress}/{str(tokenId)}/raw_metadata"
        response = requests.get(url, headers=headers).text
        
        try:
            nftMetadata = json.loads(response)
        except:
            print(tokenId)
            print(response)

        metadata.append(nftMetadata['metadata'])
        
        with open(metadataPath + contractName + '_metadata.json', "w") as file:
            json.dump(metadata, file, indent=2) 

for i in tqdm(range(len(contractAddresses))):
    print(contractNames[i] + ' started parsing.')
    do_md_request(contractAddresses[i], contractNames[i], int(contractSupplies[i]))
    print(contractNames[i] + ' finished parsing. Total supply', len(metadata))

'''
async def get(url, session, headers):
    try:
        async with session.get(url=url, headers=headers).text as response:
            resp = await response
            # print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
            return json.loads(resp)['metadata']
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))
        return None


  

async def main(urls, headers):
    metadata = []
    async with aiohttp.ClientSession() as session:
        metadata = await asyncio.gather(*[get(url, session, headers) for url in urls])
    return metadata
    #print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))

for i in range(len(contractAddresses))[1:2]:
    urls = [] 
    for tokenId in range(1, int(contractSupplies[i]) + 1):
        urls.append(f"https://ethereum-rest.api.mnemonichq.com/foundational/v1beta2/nfts/{contractAddresses[i]}/{str(tokenId)}/raw_metadata")
        metadata = asyncio.run(main(urls, headers))

        with open(metadataPath + contractNames[i] + '_metadata.json', "w") as file:
            json.dump(metadata, file, indent=2) 
'''