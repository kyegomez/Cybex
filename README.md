[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Cybex
Autonomously generate high-quality unit tests for entire repositories, just plug in and play the repo link and enjoy high quality tests to elevate your project


## Installation
`pip install cybex`


## Usage
```python
from cybex import TestGenerator

# Example usage:
test_generator = TestGenerator(
    repo_url="https://github.com/kyegomez/exa", 
    api_key=""
)
test_generator.download()
test_generator.generate_tests()
```

# License
MIT



