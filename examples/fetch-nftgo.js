import fetch from 'node-fetch';

// Replace with your NFTGo API key:
const apiKey = "54804bbd-44b7-4f50-8229-3c5fa3db2dac";
const options= {
  method: 'GET',
  headers: {
    'X-API-KEY': '54804bbd-44b7-4f50-8229-3c5fa3db2dac'
  }
};
// Replace with the contract address you want to query:
const contractAddress = "0xb452ff31b35dee74f2fdfd5194b91af1bad07b91"
/*const contractAddress = "0xc99c679c50033bbc5321eb88752e89a93e9e83c5" /*killbears*/
/*const contractAddlress = "0x86357A19E5537A8Fba9A004E555713BC943a66C0" /*neo tokyo*/

// Replace with the token id you want to query:
const tokenId = "2"
const url = `https://data-api.nftgo.io/eth/v1/nft/${contractAddress}/${tokenId}/info`;

console.log(url)

// Make the request and print the formatted response:
fetch(url, options)
  .then(res => res.json())
  .then(json => console.log(json))
  // .catch(err => console.error('error:' + err));
