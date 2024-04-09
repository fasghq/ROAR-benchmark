import {
  Collection,
  EVMContractTokenIdentifier,
  RarityRanker,
  StringTrait,
  Token,
  TokenMetadata,
  TokenStandard,
} from '@nftgo/gorarity';

function script() {
  /**
   * Assemble the traits data into Token object
   */
  const tokens = [
    new Token(
      new EVMContractTokenIdentifier('0xaaa', 1),
      TokenStandard.ERC721,
      new TokenMetadata(
        new Map()
          .set('trait1', new StringTrait('trait1', 'value1'))
          .set('trait2', new StringTrait('trait2', 'value1'))
          .set('trait3', new StringTrait('trait3', 'value1'))
      )
    ),
    new Token(
      new EVMContractTokenIdentifier('0xaaa', 2),
      TokenStandard.ERC721,
      new TokenMetadata(
        new Map()
          .set('trait1', new StringTrait('trait1', 'value1'))
          .set('trait2', new StringTrait('trait2', 'value1'))
          .set('trait3', new StringTrait('trait3', 'value1'))
      )
    ),
    new Token(
      new EVMContractTokenIdentifier('0xaaa', 3),
      TokenStandard.ERC721,
      new TokenMetadata(
        new Map()
          .set('trait1', new StringTrait('trait1', 'value2'))
          .set('trait2', new StringTrait('trait2', 'value1'))
          .set('trait3', new StringTrait('trait3', 'value3'))
      )
    ),
    new Token(
      new EVMContractTokenIdentifier('0xaaa', 4),
      TokenStandard.ERC721,
      new TokenMetadata(
        new Map()
          .set('trait1', new StringTrait('trait1', 'value2'))
          .set('trait2', new StringTrait('trait2', 'value2'))
          .set('trait3', new StringTrait('trait3', 'value3'))
      )
    ),
    new Token(
      new EVMContractTokenIdentifier('0xaaa', 5),
      TokenStandard.ERC721,
      new TokenMetadata(
        new Map()
          .set('trait1', new StringTrait('trait1', 'value3'))
          .set('trait2', new StringTrait('trait2', 'value3'))
          .set('trait3', new StringTrait('trait3', 'value3'))
      )
    ),
  ];

  /**
   * Using rankCollection method to calculate token rarity score and rank tokens according to rarity score.
   */
  const rankedTokens = RarityRanker.rankCollection(new Collection(tokens));

  for (const tokenRarity of rankedTokens) {
    const tokenId = tokenRarity.token.tokenIdentifier.tokenId;
    const rank = tokenRarity.rank;
    const score = tokenRarity.score;
    console.log(`Token ${tokenId} has rank ${rank} score ${score}`);
  }
}

script();
