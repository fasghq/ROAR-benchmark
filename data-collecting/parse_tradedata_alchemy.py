import pandas as pd
import requests
import json
from tqdm import tqdm

headers = {'accept': 'application/json'}
key = 'xkks-g1YtxL9-kRoJAGR0_CqsiVcobLR'

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
contractAddresses = collectionsDF['Address'].tolist()

tradedataPath = '/home/ubuntu/projects/unipro/models/rarity/tradedata/'

def do_request(contractAddress, contractName):
    fromBlock = '0'
    toBlock = 'latest'
    pageKey = ''
    sales = []
    initial = True
    
    #with open(contractName + '.json', "r") as file:
    #    sales = json.load(file)
    
    while True:
        if initial:
            url = ('https://eth-mainnet.g.alchemy.com/nft/v2/'+ key +
                   '/getNFTSales?fromBlock=' + fromBlock + '&toBlock=' + toBlock +
                   '&order=asc&contractAddress=' + contractAddress)
        else:
            url = ('https://eth-mainnet.g.alchemy.com/nft/v2/'+ key +
                   '/getNFTSales?fromBlock=' + fromBlock + '&toBlock=' + toBlock +
                   '&order=asc&contractAddress=' + contractAddress + '&pageKey=' + pageKey)
            
        response = requests.get(url, headers=headers).text
        
        try:
            nftSales = json.loads(response)['nftSales']
            sales += nftSales
            with open(tradedataPath + contractName + '.json', "w") as file:
                json.dump(sales, file, indent=2) 
        except:
            print('Collection', contractName, 'error.')
            print(response)
            return False
        
        try:
            pageKey = json.loads(response)['pageKey']
        except:
            print('Pages ended.')
            return sales
        initial = False
   
        if len(nftSales) != 1000:
            return sales
        
for i in tqdm(range(len(contractAddresses))[95:]):
    print(contractNames[i] + ' started parsing.')
    do_request(contractAddresses[i], contractNames[i])
    print(contractNames[i] + ' finished parsing.')