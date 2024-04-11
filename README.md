# ROAR

A Benchmark for NFT Rarity Meters.


## Installation

```console
# Clone a repo
git clone https://github.com/fasghq/ROAR-benchmark.git

# Create virtual envoronment and install required packages
python3 -m venv roar-venv
source roar-venv/bin/activate
pip3 install -r requirements.txt
```

## Verification of rarity meters implementations

As part of our benchmark showcase, we also performed a set of verification experiments to ensure the accuracy of our implementation.
Custom implementations of `OpenRarity`, `rarity.tools`, `NFTGo` and `Kramer` can be found in the `performance_evaluation` directory. 

The command for running verification tests:

```console
python -m pytest examples
```

## Results

TODO


## Citation

TODO
