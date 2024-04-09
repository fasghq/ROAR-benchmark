import copy
import dataclasses
import pandas as pd
import json
import time
import typing as tp
import performance_evaluation.openrarity_score as openrarity
import performance_evaluation.raritytools_score as raritytools
from performance_evaluation.openrarity_score import openRarityScore
from performance_evaluation.raritytools_score import rarityToolsScore

import pytest

from pytest import approx

metadata_path = 'dataset/metadata'


@dataclasses.dataclass
class OpenRarityCase:
    collectionName: str
    tokenToRarity: tp.Mapping[int, int]


OPEN_RARITY_CASES = [
    OpenRarityCase(
        collectionName='MICE',
        tokenToRarity={
            1305: 9031,
            4498: 9204,
            5100: 3213,
            5493: 2712,
            580:  5365
        }
    ),
    OpenRarityCase(
        collectionName='thelittlesnft',
        tokenToRarity={
            6733: 5818,
            1286: 7271,
            6573: 6496,
            2448: 4928,
            9859: 9325
        }
    )
]


@pytest.mark.parametrize('case', OPEN_RARITY_CASES)
def test_open_rarity(case: OpenRarityCase) -> None:
    path = metadata_path + '/' + case.collectionName + '_metadata.json'
    with open(path, 'r') as file:
        metadataDF, _ = openrarity.metadataJsonToDF(json.load(file))
    scores = openRarityScore(metadataDF)

    tokens = sorted(
        list(case.tokenToRarity.keys()),
        key=lambda x: scores[scores['Token Id'] == str(x)]['Rarity score'].item(),
        reverse=True
    )

    correct = list(map(lambda x: x[0], sorted(case.tokenToRarity.items(), key=lambda x: x[1])))

    assert tokens == correct
