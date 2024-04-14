import os
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

def kramerScore(traits_data, collection_symbol):
    tokenIdColumn = traits_data['Token Id']
    try:
        traits_data = traits_data.drop('Token ID', axis=1)
    except:
        pass
    else:
        print(collection_symbol)
    
    traits_data = traits_data.drop('Token Id', axis=1)
    traits_data = traits_data.replace(np.nan, "None")
    rarityScores = pd.DataFrame(traits_data.copy(deep=True))
    
    traitScores = {}
    for attribute in traits_data.columns:
        value_scores = []
        attribute_values = traits_data[attribute].value_counts().index.tolist()
        value_counts = traits_data[attribute].value_counts()
        #if attribute == 'prime':
        #    traitScores[attribute] = dict(zip(attribute_values, [1/2] * 28170))
        #   continue
        if len(attribute_values) == 1:
            traitScores[attribute] = dict(zip(attribute_values, [0]))
            continue
        for i in range(len(value_counts)):
            value_score = []
            for j in range(len(value_counts)):
                if i != j:
                    value_score.append(value_counts.iloc[j] / (value_counts.iloc[i] + value_counts.iloc[j]))
            value_score = np.array(value_score)
            value_scores.append(np.average(value_score))
        normalization = np.sum(np.multiply(value_scores, value_counts)) / np.sum(value_counts)
        value_scores /= normalization
        traitScores[attribute] = dict(zip(attribute_values, value_scores))
        
    for attribute in rarityScores.columns:
        try:
            rarityScores[attribute] = rarityScores[attribute].map(traitScores[attribute]).fillna(rarityScores[attribute])
        except:
            print(attribute)
            continue
    rarityScores['Rarity score'] = rarityScores.sum(axis="columns")
    rarityScores['Token Id'] = tokenIdColumn
    return rarityScores


metadataPath = 'dataset/metadata'
onlyfiles = natsorted([f for f in listdir(metadataPath) if isfile(join(metadataPath, f))])
# onlyfiles = ['XBORG_metadata.json']

kramerScoresPath = 'results/kramer_scores'

if __name__ == '__main__':
    problems = {}
    for fileName in tqdm(onlyfiles):
        print(f"{fileName.split('_')[0]} - start processing.")
        with open(metadataPath + '/' + fileName, 'r') as file:
            metadataDF, collection_problems = metadataJsonToDF(json.load(file))
            problems[fileName[:fileName.find("_")]] = collection_problems
        scores = kramerScore(metadataDF, fileName[:fileName.find("_")]) 
        if not os.path.isdir(kramerScoresPath):
                os.mkdir(kramerScoresPath)
        scores.to_csv(kramerScoresPath + '/' + fileName[:fileName.find("_")] + '_kramer_scores.csv')
        
    with open('problems.json', "w") as file:
        json.dump(problems, file, indent=2) 

#CAT~13, COOL-19, NEOTI-65, NEOTOI-66, POETS-74
#main:main, body:blue cat skin, Status:First Citizen, Status:Outer Citizen, influence:... - all values same => 0
#POETS prime - all unique values => 1/2