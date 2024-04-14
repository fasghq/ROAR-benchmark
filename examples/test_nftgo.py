import dataclasses
import json
import typing as tp
import performance_evaluation.nftgo_score as nftgo

import pytest

from pytest import approx

metadata_path = 'dataset/metadata'


@dataclasses.dataclass
class NFTGoCase:
    collectionName: str
    tokenToRank: tp.Mapping[int, int]


NFT_GO_CASES = [
    NFTGoCase(
        collectionName='XBorg',
        tokenToRank={
            1253: 2001,
            2326: 684,
            187: 1250,
            1257: 1159,
            1254: 1020
        }
    )
]


@pytest.mark.parametrize('case', NFT_GO_CASES)
def test_nftgo_rarity(case: NFTGoCase) -> None:
    path = metadata_path + '/' + case.collectionName + '_metadata.json'
    with open(path, 'r') as file:
        metadataDF, _ = nftgo.metadataJsonToDF(json.load(file))
    scores = nftgo.nftGoScore(metadataDF)

    tokens = sorted(
        list(case.tokenToRank.keys()),
        key=lambda x: scores[scores['Token Id'] == str(x)]['Rarity score'].item(),
        reverse=True
    )

    correct = list(map(lambda x: x[0], sorted(case.tokenToRank.items(), key=lambda x: x[1])))

    assert tokens == correct