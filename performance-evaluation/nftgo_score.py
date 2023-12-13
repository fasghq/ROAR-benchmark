from os import listdir
from os.path import isfile, join
from collections import ChainMap
import pandas as pd
import numpy as np
from natsort import natsorted
from tqdm import tqdm
import json
from multiprocessing import Pool


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

def loop_for_i(index_i, token_i):
    global traits_data
    JD_i = []
    for index_j, token_j in traits_data.iterrows():
        if index_i == index_j:
            continue
        intersection = 0
        for attribute in traits_data.columns:
            if token_i[attribute] == token_j[attribute]:
                intersection += 1
        union = 2 * len(traits_data.columns) - intersection
        JD_i_j = intersection / union
        JD_i.append(1 - JD_i_j)
    token_score = np.average(np.array(JD_i))
    return token_score

def init_worker(data):
    global traits_data
    traits_data = data

def nftGoScore(traits_data):
    tokenIdColumn = traits_data['Token Id']
    traits_data = traits_data.drop('Token Id', axis=1)
    traits_data = traits_data.replace(np.nan, "None")
    token_scores = []
    '''
    for index_i, token_i in traits_data.iterrows():
        JD_i = []
        for index_j, token_j in traits_data.iterrows():
            if index_i == index_j:
                continue
            intersection = 0
            for attribute in traits_data.columns:
                if token_i[attribute] == token_j[attribute]:
                    intersection += 1
            union = 2 * len(traits_data.columns) - intersection
            JD_i_j = intersection / union
            JD_i.append(1 - JD_i_j)
        token_scores.append(np.average(np.array(JD_i)))
    '''
    args = []
    for index_i, token_i in traits_data.iterrows():
        args.append((index_i, token_i))
    with Pool(initializer=init_worker, initargs=(traits_data,)) as pool:
        token_scores = pool.starmap(loop_for_i, args)

    min_val, max_val = min(token_scores), max(token_scores)
    normalized_scores = [((x - min_val) / (max_val - min_val)) * 100. for x in token_scores]
    traits_data['Rarity score'] = normalized_scores
    traits_data['Token Id'] = tokenIdColumn    
    return traits_data


metadataPath = '/home/ubuntu/projects/unipro/models/rarity/metadata'
onlyfiles = natsorted([f for f in listdir(metadataPath) if isfile(join(metadataPath, f))])

nftGoScoresPath = '/home/ubuntu/projects/unipro/models/rarity/nftgo_scores'

problems = {}
for fileName in tqdm(onlyfiles[5:6]):
    print(f"{fileName.split('_')[0]} - start processing.")
    ''''''
    with open(metadataPath + '/' + fileName, 'r') as file:
        metadataDF, collection_problems = metadataJsonToDF(json.load(file))
        problems[fileName[:fileName.find("_")]] = collection_problems
    scores = nftGoScore(metadataDF) 
    scores.to_csv(nftGoScoresPath + '/' + fileName[:fileName.find("_")] + '_nftgo_scores.csv')
    
with open('problems.json', "w") as file:
    json.dump(problems, file, indent=2) 
