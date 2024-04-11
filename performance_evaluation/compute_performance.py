import numpy as np
import pandas as pd
import json
from scipy.optimize import LinearConstraint, minimize
from tqdm import tqdm

def salesJsonToNP(tradedataJson):
    sales = []
    for trade in tradedataJson:
        sale = [int(trade['tokenId']), int(trade['blockNumber'])]
        price = 0
        for fee in ['sellerFee', 'protocolFee', 'royaltyFee']:
            if trade[fee]:
                price += float(trade[fee]['amount'])
        sale.append(price)
        sales.append(sale)
    sales = np.array(sales)
    sales = sales[sales[:, 2] != 0]
    return sales

def scoresDFsToDict(scoresDF_raritytools, scoresDF_kramer, scoresDF_opentarity, scoresDF_nftgo):
    idsNP = scoresDF_raritytools['Token Id'].to_list()
    attributesNP_raritytools = scoresDF_raritytools.drop(['Token Id', 'Rarity score'], axis=1).to_numpy(dtype=np.float64)
    attributesNP_kramer = scoresDF_kramer.drop(['Token Id', 'Rarity score'], axis=1).to_numpy(dtype=np.float64)
    attributesNP_opentarity = scoresDF_opentarity.drop(['Token Id', 'Rarity score'], axis=1).to_numpy(dtype=np.float64)
    attributesNP_nftgo = scoresDF_nftgo['Rarity score'].to_numpy(dtype=np.float64)
    attributesNP_nftgo = attributesNP_nftgo.reshape(len(attributesNP_nftgo), 1)
    attributesNP = np.concatenate((attributesNP_raritytools, attributesNP_kramer, attributesNP_opentarity, attributesNP_nftgo), axis=1)
    idToScoreDict = {idsNP[i]: attributesNP[i] for i in range(len(idsNP))}
    del idsNP
    del attributesNP
    return idToScoreDict

def scoresDFToDict(scoresDF, rarity_meter='raritytools', mode='train'):
    idsNP = scoresDF['Token Id'].to_list()
    if rarity_meter == 'openrarity' and mode == 'test_basic':
        attributesNP = scoresDF.drop(['Token Id', 'Rarity score', 'Trait count information value', 'Unique Trait count'], axis=1).to_numpy(dtype=np.float64)
    elif rarity_meter == 'openrarity' and mode == 'test_trait_count':
        attributesNP = scoresDF.drop(['Token Id', 'Rarity score', 'Unique Trait count'], axis=1).to_numpy(dtype=np.float64)
    elif rarity_meter == 'openrarity' and mode == 'test_unique_trait_count':
        attributesNP = scoresDF.drop(['Token Id', 'Rarity score', 'Trait count information value'], axis=1).to_numpy(dtype=np.float64)
    elif rarity_meter == 'nftgo':
        attributesNP = scoresDF['Rarity score'].to_numpy(dtype=np.float64)
        attributesNP = attributesNP.reshape(len(attributesNP), 1)
    else:
        attributesNP = scoresDF.drop(['Token Id', 'Rarity score'], axis=1).to_numpy(dtype=np.float64)

    idToScoreDict = {idsNP[i]: attributesNP[i] for i in range(len(idsNP))}
    del idsNP
    del attributesNP
    return idToScoreDict

def getSalePairs(salesNP, blocksPerOneDay=6000, numberOfDays=7):
    length = int(np.ceil(len(salesNP) * (len(salesNP) - 1) / 2))
    salePairs = np.zeros((length, 6), dtype=np.float64)
    index = 0
    for i in range(len(salesNP)):
        sale_i = salesNP[i]
        for j in range(i + 1, len(salesNP)):
            sale_j = salesNP[j]
            if abs(sale_i[1] - sale_j[1]) <= blocksPerOneDay * numberOfDays:
                if sale_i[0] != sale_j[0]:
                    salePairs[index] = np.array([sale_i[0], sale_j[0], sale_i[1], sale_j[1], sale_i[2], sale_j[2]])
                    index += 1
            else:
                break
    salePairs = salePairs[salePairs[:, 2] != 0]
    return salePairs
            
def relativeRarity(salePairs, idToScoreDict):
    attributes_count = len(idToScoreDict[list(idToScoreDict.keys())[0]])
    rarityMatrix1 = np.zeros((len(salePairs), attributes_count))
    rarityMatrix2 = np.zeros((len(salePairs), attributes_count))
    for index in range(len(salePairs)):
        rarityMatrix1[index] = idToScoreDict[salePairs[index, 0]]
        rarityMatrix2[index] = idToScoreDict[salePairs[index, 1]]
    return rarityMatrix1, rarityMatrix2
    #return np.log(np.divide((1 + rarityMatrix1.sum(axis=1)), (1 + rarityMatrix2.sum(axis=1))))

def relativePrice(priceVector1, priceVector2):
    return np.log(np.divide(priceVector1, priceVector2))

def kernelEpanechnikov(deltasVector, blocksPerOneDay=6000, dayLimit=7):
    blockNumberLimit = dayLimit * blocksPerOneDay
    return 3 / 4 * (np.power(1 - np.abs(deltasVector) / blockNumberLimit, 2))

def weightedCorrelation(X, Y, W):
    X_dev = X - np.average(X, weights=W)
    Y_dev = Y - np.average(Y, weights=W)
    numerator  = np.sum(W * X_dev * Y_dev) 
    denominatorX = np.sqrt(np.sum(W * np.power(X_dev, 2)))
    denominatorY = np.sqrt(np.sum(W * np.power(Y_dev, 2)))
    denominator = denominatorX * denominatorY
    return numerator / denominator

def objectiveToMinimize(coefficientsVector, rarityMatrix1, rarityMatrix2, relativePriceVector, weightsVector):
    rarityMatrix1 = coefficientsVector * rarityMatrix1
    rarityMatrix2 = coefficientsVector * rarityMatrix2
    relativeRarityVector = np.log(np.divide((1 + rarityMatrix1.sum(axis=1)), (1 + rarityMatrix2.sum(axis=1))))
    return -weightedCorrelation(relativeRarityVector, relativePriceVector, weightsVector)
   
def generatePermutations(n):
    return np.concatenate((np.eye(n, dtype=int), np.ones(n, dtype=int)[np.newaxis, :]), axis=0)

def computePerformance(contractName, mode='train', rarity_meter='raritytools'):
    print('Getting sale pairs...')
    with open(f'{tradedataPath}/{contractName}.json', "r") as file:
        salesNP = salesJsonToNP(json.load(file))
    if contractName == 'BEANZ':
        sep_id = int(np.ceil(0.965 * len(salesNP))) # 0.965 0.6
    else:
        sep_id = int(np.ceil(0.9 * len(salesNP))) # 0.9 0.5
    train_id = int(sep_id + np.floor(0.7 * (len(salesNP) - sep_id)))
    if mode in ['train_vanilla', 'train_opt']:
        salesNP = salesNP[sep_id:train_id, :]
    else:
        salesNP = salesNP[train_id:, :]
    salePairs = getSalePairs(salesNP)
    print('Sale pairs number:', len(salePairs[:, 0]), len(salesNP[:, 0]))
    del salesNP

    print('Getting rarity matrices...')
    
    if rarity_meter == 'roar':
        scoresDF_raritytools = pd.read_csv(f"{scoresPaths['raritytools']}/{contractName}_{'raritytools'}_scores.csv", index_col=0)
        scoresDF_kramer = pd.read_csv(f"{scoresPaths['kramer']}/{contractName}_{'kramer'}_scores.csv", index_col=0)
        scoresDF_opentarity = pd.read_csv(f"{scoresPaths['openrarity']}/{contractName}_{'openrarity'}_scores.csv", index_col=0)
        scoresDF_nftgo = pd.read_csv(f"{scoresPaths['nftgo']}/{contractName}_{'nftgo'}_scores.csv", index_col=0)
        idToScoreDict = scoresDFsToDict(scoresDF_raritytools, scoresDF_kramer, scoresDF_opentarity, scoresDF_nftgo)
    else:
        scoresDF = pd.read_csv(f'{scoresPaths[rarity_meter]}/{contractName}_{rarity_meter}_scores.csv', index_col=0)
        idToScoreDict = scoresDFToDict(scoresDF, rarity_meter=rarity_meter, mode=mode)
    #relativeRarityVector = relativeRarity(salePairs, idToScoreDict)
    rarityMatrix1, rarityMatrix2 = relativeRarity(salePairs, idToScoreDict)
    del idToScoreDict

    print('Getting relative price vector...')
    relativePriceVector = relativePrice(salePairs[:, 4], salePairs[:, 5])
    print('Getting weights vector...')
    weightsVector = kernelEpanechnikov(salePairs[:, 2] - salePairs[:, 3])
    del salePairs

    if mode == 'test_opt':
        print('Calculating correlation...')
        with open(f"{corrPaths[rarity_meter]['train_opt']}/{contractName}_{rarity_meter}_corr_train.json", "r") as file:
            minimizationResults = json.load(file)
            coefficientsVector = minimizationResults['x']
        return objectiveToMinimize(coefficientsVector, rarityMatrix1, rarityMatrix2, relativePriceVector, weightsVector)
    elif mode in ['test_vanilla', 'test_basic', 'test_trait_count', 'test_unique_trait_count', 'train_vanilla']:
        print('Calculating correlation...')
        coefficientsVector = [1] * len(rarityMatrix1[0])
        return objectiveToMinimize(coefficientsVector, rarityMatrix1, rarityMatrix2, relativePriceVector, weightsVector)

    print('Getting linear constraints...')
    numberOfFreeCoefficients = len(rarityMatrix1[0])
    linearConstraints = []
    linearConstraints.append(generatePermutations(numberOfFreeCoefficients))
    linearConstraints.append(np.full(numberOfFreeCoefficients + 1, 0))
    linearConstraints.append(np.full(numberOfFreeCoefficients + 1, 1))
    linearConstraints = LinearConstraint(linearConstraints[0], linearConstraints[1], linearConstraints[2])
    coefficientsStart = np.full(numberOfFreeCoefficients, 1 / numberOfFreeCoefficients)

    print('Starting minimization...')
    minimizationResults = minimize(
        objectiveToMinimize, x0=coefficientsStart,
        args=(rarityMatrix1, rarityMatrix2, relativePriceVector, weightsVector),
        constraints=linearConstraints, options={'disp': True},
    )

    return minimizationResults
    

metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata'
tradedataPath = '/home/ubuntu/projects/unipro/models/rarity/tradedata'

scoresPaths = {
    'raritytools': '/home/ubuntu/projects/unipro/models/rarity/raitytools_scores',
    'kramer': '/home/ubuntu/projects/unipro/models/rarity/kramer_scores',
    'openrarity': '/home/ubuntu/projects/unipro/models/rarity/openrarity_scores',
    'nftgo': '/home/ubuntu/projects/unipro/models/rarity/nftgo_scores'
}

corrPaths = {
    'raritytools': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_train_opt',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_test_vanilla',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_test_opt'
    },
    'kramer': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_train_opt',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_test_vanilla',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/kramer_corr_test_opt'
    },
    'openrarity': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_train_vanilla',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_train',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_vanilla50',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_opt',
        'test_basic': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_basic50',
        'test_trait_count': '/home/ubuntu/projects/unipro/models/rarity/openrarity_corr_test_trait_count50',
        'test_unique_trait_count': '/home/ubuntu/projects/unipro/models/rarity/openrarity_test_unique_trait_count50'
    },
    'nftgo': {
        'train_vanilla': '/home/ubuntu/projects/unipro/models/rarity/nftgo_corr_train_vanilla',
        'test_vanilla': '/home/ubuntu/projects/unipro/models/rarity/nftgo_corr_test_vanilla'
    },
    'roar': {
        'train': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_train',
        'train_opt': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_train_opt99',
        'test_vanilla': '',
        'test_opt': '/home/ubuntu/projects/unipro/models/rarity/roar_corr_test_opt'
    }
}

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')
contractNames = collectionsDF['Symbol'].tolist()
#contractNames = ['NKMGS']
failed = {}

rarity_meter = 'openrarity'
mode = 'test_unique_trait_count'

for contractName in tqdm(contractNames):
    print(f"{contractName} - start processing.")
    ''''''
    if mode == 'train':
        try:
            minimizationResults = computePerformance(contractName, mode=mode, rarity_meter=rarity_meter)
            resultsDict = {
                'x': minimizationResults.x.tolist(), 
                'fun': minimizationResults.fun, 
                'success': bool(minimizationResults.success),
                'message': minimizationResults.message,
                'jac': minimizationResults.jac.tolist(),
                'nit': minimizationResults.nit,
                'nfev': minimizationResults.nfev,
                'njev': minimizationResults.njev,
                'status': minimizationResults.status
            }

            with open(f'{corrPaths[rarity_meter][mode]}/{contractName}_{rarity_meter}_corr_{mode}.json', "w") as file:
                json.dump(resultsDict, file, indent=2) 
        except:
            failed[contractName] = 1
    else:
        try:
            corr = computePerformance(contractName, mode=mode, rarity_meter=rarity_meter)
            with open(f'{corrPaths[rarity_meter][mode]}/{contractName}_{rarity_meter}_corr_{mode}.json', "w") as file:
                json.dump({'fun': corr}, file, indent=2) 
        except:
            failed[contractName] = 1
    
if len(failed) > 0:
    with open('failed_corr.json', "w") as file:
        json.dump(failed, file, indent=2) 


