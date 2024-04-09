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
class RarityToolsCase:
    collectionName: str
    token_id: int
    expected_rarity_score: float


RARITY_TOOLS_CASES = [
    RarityToolsCase(
        collectionName='VFT',
        token_id=6874,
        expected_rarity_score=approx(10954.81, abs=1e-2)
    ),
    # RarityToolsCase(
    #     collectionName='ALIENFRENS',
    #     token_id=1746,
    #     expected_rarity_score=approx(1444.46, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='ALIENFRENS',
    #     token_id=6699,
    #     expected_rarity_score=approx(1110.53, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='ALIENFRENS',
    #     token_id=8232,
    #     expected_rarity_score=approx(531.74, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='ALIENFRENS',
    #     token_id=8574,
    #     expected_rarity_score=approx(246.13, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='ALIENFRENS',
    #     token_id=2110,
    #     expected_rarity_score=approx(430.11, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='GROUPIE',
    #     token_id=127,
    #     expected_rarity_score=approx(17025.14, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='GROUPIE',
    #     token_id=4988,
    #     expected_rarity_score=approx(516.81, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='GROUPIE',
    #     token_id=8760,
    #     expected_rarity_score=approx(442.05, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='GROUPIE',
    #     token_id=6468,
    #     expected_rarity_score=approx(394.56, abs=1e-2)
    # ),
    # RarityToolsCase(
    #     collectionName='GROUPIE',
    #     token_id=2268,
    #     expected_rarity_score=approx(243.43, abs=1e-2)
    # )
]



@pytest.mark.parametrize('case', RARITY_TOOLS_CASES)
def test_rarity_tools(case: RarityToolsCase) -> None:
    path = metadata_path + '/' + case.collectionName + '_metadata.json'
    with open(path, 'r') as file:
        metadataDF, _ = raritytools.metadataJsonToDF(json.load(file))
    scores = raritytools.rarityToolsScore(metadataDF)
    rarity_score = scores[scores['Token Id'] == str(case.token_id)]['Rarity score'].item()

    assert rarity_score == case.expected_rarity_score
