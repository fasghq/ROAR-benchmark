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


def rarityToolsScore(traits_data, weighted=False):
    tokenIdColumn = traits_data['Token Id']
    traits_data = traits_data.drop('Token Id', axis=1)
    if not('Trait count' in traits_data.columns):
        traits_data['Trait count'] = traits_data.count(axis=1)
    traits_data = traits_data.replace(np.nan, "None")
    rarity_values = {}
    for attribute in traits_data.columns:
        value_counts = traits_data[attribute].value_counts()
        total_token_count = len(traits_data)
        if weighted is False:
            rarity = 1 / (value_counts / total_token_count)
        elif weighted is True:
            rarity = total_token_count / (value_counts * len(value_counts))
        rarity_values[attribute + ' rarity score'] = traits_data[attribute].map(rarity)

    rarityScores = pd.DataFrame(rarity_values)
    rarityScores['Rarity score'] = rarityScores.sum(axis="columns")
    rarityScores['Token Id'] = tokenIdColumn
    return rarityScores

metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata'
onlyfiles = natsorted([f for f in listdir(metadataPath) if isfile(join(metadataPath, f))])

rarityToolsScoresPath = '/home/ubuntu/projects/unipro/models/rarity/raitytools_scores'

problems = {}
for fileName in tqdm(onlyfiles[1:]):
    print(f"{fileName.split('_')[0]} - start processing.")
    with open(metadataPath + '/' + fileName, 'r') as file:
        metadataDF, collection_problems = metadataJsonToDF(json.load(file))
        problems[fileName[:fileName.find("_")]] = collection_problems
    scores = rarityToolsScore(metadataDF) 
    scores.to_csv(rarityToolsScoresPath + '/' + fileName[:fileName.find("_")] + '_raritytools_scores.csv')

with open('problems.json', "w") as file:
    json.dump(problems, file, indent=2) 