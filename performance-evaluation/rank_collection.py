import pandas as pd


scoresPaths = {
    'raritytools': '/home/ubuntu/projects/unipro/models/rarity/rarity_scores/raitytools_scores',
    'kramer': '/home/ubuntu/projects/unipro/models/rarity/rarity_scores/kramer_scores',
    'openrarity': '/home/ubuntu/projects/unipro/models/rarity/rarity_scores/openrarity_scores',
    'nftgo': '/home/ubuntu/projects/unipro/models/rarity/rarity_scores/nftgo_scores'
}

ranksPaths = {
    'raritytools': '/home/ubuntu/projects/unipro/models/rarity/rarity_ranks/raritytools_ranks',
    'kramer': '/home/ubuntu/projects/unipro/models/rarity/rarity_ranks/kramer_ranks',
    'openrarity': '/home/ubuntu/projects/unipro/models/rarity/rarity_ranks/openrarity_ranks',
    'nftgo': '/home/ubuntu/projects/unipro/models/rarity/rarity_ranks/nftgo_ranks'
}

rarity_meters = list(scoresPaths.keys())

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')
contractNames = collectionsDF['Symbol'].tolist()

for rarity_meter in rarity_meters:
    for contractName in contractNames:
        scoresDF = pd.read_csv(f'{scoresPaths[rarity_meter]}/{contractName}_{rarity_meter}_scores.csv')
        ranksDF = scoresDF[['Token Id', 'Rarity score']]
        ranksDF['Rank'] = ranksDF['Rarity score'].rank(method='min', ascending=False)
        ranksDF.to_csv(f'{ranksPaths[rarity_meter]}/{contractName}_{rarity_meter}_ranks.csv', index=False)
