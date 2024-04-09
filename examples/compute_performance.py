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

def scoresDFToDict(scoresDF):
    idsNP = scoresDF['Token Id'].to_list()
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
    rarityMatrix1 = np.zeros((len(salePairs), len(idToScoreDict[1])))
    rarityMatrix2 = np.zeros((len(salePairs), len(idToScoreDict[1])))
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

def computePerformance(contractName, mode='train'):
    print('Getting sale pairs...')
    with open(tradedataPath + '/' + contractName + '.json', "r") as file:
        salesNP = salesJsonToNP(json.load(file))
    sep_id = int(np.ceil(0.9 * len(salesNP)))
    train_id = int(sep_id + np.floor(0.7 * (len(salesNP) - sep_id)))
    if mode == 'train':
        salesNP = salesNP[sep_id:train_id, :]
    else:
        salesNP = salesNP[train_id:, :]
    salePairs = getSalePairs(salesNP)
    print('Sale pairs number:', len(salePairs[:, 0]), len(salesNP[:, 0]))
    del salesNP

    print('Getting rarity matrices...')
    scoresDF = pd.read_csv(raritytoolsScoresPath + '/' + contractName + '_raritytools_scores.csv', index_col=0)
    idToScoreDict = scoresDFToDict(scoresDF)
    #relativeRarityVector = relativeRarity(salePairs, idToScoreDict)
    rarityMatrix1, rarityMatrix2 = relativeRarity(salePairs, idToScoreDict)
    del idToScoreDict

    print('Getting relative price vector...')
    relativePriceVector = relativePrice(salePairs[:, 4], salePairs[:, 5])
    print('Getting weights vector...')
    weightsVector = kernelEpanechnikov(salePairs[:, 2] - salePairs[:, 3])
    del salePairs

    print('Getting linear constraints...')
    numberOfFreeCoefficients = len(rarityMatrix1[0])
    linearConstraints = []
    linearConstraints.append(generatePermutations(numberOfFreeCoefficients))
    linearConstraints.append(np.full(numberOfFreeCoefficients + 1, 0))
    linearConstraints.append(np.full(numberOfFreeCoefficients + 1, 1))
    linearConstraints = LinearConstraint(linearConstraints[0], linearConstraints[1], linearConstraints[2])
    coefficientsStart = np.full(numberOfFreeCoefficients, 1 / numberOfFreeCoefficients) # 1 / numberOfFreeCoefficients

    print('Starting minimization...')
    minimizationResults = minimize(
        objectiveToMinimize, x0=coefficientsStart,
        args=(rarityMatrix1, rarityMatrix2, relativePriceVector, weightsVector),
        constraints=linearConstraints, options={'disp': True},
    )

    return minimizationResults
    

metadataPath = 'dataset/metadata' # '/home/ubuntu/projects/unipro/models/rarity/metadata'
tradedataPath = 'dataset/tradedata' # '/home/ubuntu/projects/unipro/models/rarity/tradedata'
raritytoolsScoresPath = 'raritytools_scores' # '/home/ubuntu/projects/unipro/models/rarity/raitytools_scores'
openRarityScoresPath = 'results/openrarity_scores' # '/home/ubuntu/projects/unipro/models/rarity/openrarity_scores'
kramerScoresPath = '/home/ubuntu/projects/unipro/models/rarity/kramer_scores'
nftGoScoresPath = 'results/nftgo_scores' #/home/ubuntu/projects/unipro/models/rarity/nftgo_scores'
raritytoolsCorrTrainPath = '/home/ubuntu/projects/unipro/models/rarity/raritytools_corr_train'

collectionsDF = pd.read_csv(
    '/home/ubuntu/projects/unipro/models/rarity/100NFTCollections - 100NFT_UPD.csv',
    names=['Collection', 'Symbol', 'Address', 'Total Supply'],
    header=None
).drop(0, axis='index')

contractNames = collectionsDF['Symbol'].tolist()
failed = {} # BEANZ-10
for contractName in tqdm(contractNames):
    print(f"{contractName} - start processing.")
    ''''''
    try:
        minimizationResults = computePerformance(contractName, mode='train')
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

        with open(raritytoolsCorrTrainPath + '/' + contractName + '_raritytools_corr_train.json', "w") as file:
            json.dump(resultsDict, file, indent=2) 
    except:
        failed[contractName] = 1
    
if len(failed) > 0:
    with open('failed_raritytools_corr_train.json', "w") as file:
        json.dump(failed, file, indent=2) 


