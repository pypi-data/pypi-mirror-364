# pybae
A backend library for your application

## Description
`pybae` is a Python library designed to simplify configuration and backend management in your applications. It provides tools to faster new deployments of backend services.


## Installation

Clone the repository and install the dependencies:
```bash
pip install pybae
```

## Usage

Example usage:
```python
from pybae import config

class Foo(config.ConfigSection):
    bar: str
   
class Config(config.BaseConfig)
    foo: Foo

cfg = Config.load('path/to/config.yaml')
print(cfg.foo.bar)
```

## Project Structure

- `pybae/`: library source code
  - `config.py`: configuration management
- `example/`: usage examples
  - `config.yaml`: sample configuration file
  - `example_test.py`: example test

## Testing

To run the tests:
```bash
python example/example_test.py
```

## Contributing

Contributions are welcome! Open an issue or submit a pull request for suggestions, bug reports, or new features.

## License

This project is licensed under the MIT License.

