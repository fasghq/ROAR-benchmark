from os import listdir
from os.path import isfile, join
from collections import ChainMap
import pandas as pd
import numpy as np
from natsort import natsorted
from tqdm import tqdm
import json


def metadataJsonToDF(metadata):
    traits = []
    problems = {'No Traits tokens': [], 'Wrong Traits format tokens': []}
    for token in metadata:
        if token['traits']:
            token['traits'].append({'value': token['collectionTokenId'], 'trait_type': 'Token Id'})
            trait_list = []
            for d in token['traits']:
                try:
                    trait_list.append({d['trait_type']: d['value']})
                except:
                    problems['Wrong Traits format tokens'].append(token['collectionTokenId'])
                    trait_list.append({'Noname Trait': d['value']})
            traits.append([dict(ChainMap(*trait_list))])
        else:
            problems['No Traits tokens'].append(token['collectionTokenId'])
            token['traits'].append({'value': token['collectionTokenId'], 'trait_type': 'Token Id'})
            traits.append([dict(ChainMap(*[{d['trait_type']: d['value']} for d in token['traits']]))])
    traitsDF = pd.concat([pd.DataFrame(trait) for trait in traits]).reset_index(drop=True)
    return traitsDF, problems


def countUniqueTraits(traits_data):
    uniqueTraitCount = [0 for _ in range(len(traits_data))]
    for attribute in traits_data.columns[:-1]:
        duplicates = traits_data[attribute].duplicated(keep=False)
        duplicates = duplicates[duplicates == False]
        if not duplicates.empty:
            unique_values_ids = duplicates.index
            for id in unique_values_ids:
                uniqueTraitCount[id] += 1
    return uniqueTraitCount


def openRarityScore(traits_data):
    tokenIdColumn = traits_data['Token Id']
    traits_data = traits_data.drop('Token Id', axis=1)
    if not('Trait count' in traits_data.columns):
        traits_data['Trait count'] = traits_data.count(axis=1)
    traits_data = traits_data.replace(np.nan, "None")

    uniqueTraitCount = countUniqueTraits(traits_data)

    informationValues = {}
    #expectedValues = {}
    total_token_count = len(traits_data)
    total_attribute_count = len(traits_data.columns)

    for attribute in traits_data.columns:
        value_counts = traits_data[attribute].value_counts()
        prob = value_counts / total_token_count
        logProb = (1 / prob).apply(np.log2)
        expectInform = logProb
        #expectNorm = prob * logProb
        informationValues[attribute + ' information value'] = traits_data[attribute].map(expectInform)
        #expectedValues[attribute + ' expected value'] = traits_data[attribute].map(expectNorm)

    rarityScores = pd.DataFrame(informationValues)
    #normScores = pd.DataFrame(expectedValues)
    #rarityScores['Rarity score'] = rarityScores.sum(axis="columns") / normScores.sum().sum()

    rarityScores['Information content'] = rarityScores.sum(axis="columns")
    rarityScores['Norm factor'] = rarityScores.sum(axis="columns").sum(axis="rows") / total_token_count
    rarityScores['Unique Trait count'] = uniqueTraitCount 
    rarityScores['Token Id'] = tokenIdColumn
    rarityScores['Rarity score'] = (rarityScores['Information content'] + rarityScores['Unique Trait count'] * (total_attribute_count - 1) * np.log2(total_token_count)) / rarityScores['Norm factor']
    rarityScores = rarityScores.drop(['Information content', 'Norm factor'], axis=1)
    return rarityScores


metadataPath = 'dataset/metadata'
openRarityScoresPath = 'results/scores/openrarity_scores'
onlyfiles = natsorted([f for f in listdir(metadataPath) if isfile(join(metadataPath, f))])

if __name__ == '__main__':
    problems = {}
    for fileName in tqdm(onlyfiles):
        print(f"{fileName.split('_')[0]} - start processing.")
        with open(metadataPath + '/' + fileName, 'r') as file:
            metadataDF, collection_problems = metadataJsonToDF(json.load(file))
            problems[fileName[:fileName.find("_")]] = collection_problems
        scores = openRarityScore(metadataDF) 
        scores.to_csv(openRarityScoresPath + '/' + fileName[:fileName.find("_")] + '_openrarity_scores.csv')

    with open('problems.json', "w") as file:
        json.dump(problems, file, indent=2) 
