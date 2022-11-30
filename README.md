# Sentinel Network

This is core Sentinel server infrastructure library implementing common
functionalities for all Sentinel boxes such as: 

- ZMQ networking
- Common configuration framework
- Logging in standardized way (necessary to handle log messages by TM - Turris
  Monitoring)
- Message queue for handling messages in safe and good-performing way
- Boxes monitoring


## Dependencies

- [pyzmq](https://pyzmq.readthedocs.io/en/latest) - Python bindings for ØMQ
- [msgpack](https://msgpack-python.readthedocs.io/en/latest/index.html) - MessagePack
(an efficient binary serialization format) for Python

Build system, dependency management, packaging:
- [Poetry](https://python-poetry.org/)

Dev tools:
- [black](https://github.com/psf/black)
- [isort](https://pycqa.github.io/isort/index.html)
- [Flake8-pyproject](https://github.com/john-hen/Flake8-pyproject)
- [mypy](http://www.mypy-lang.org/)

Tests:
- [pytest](https://docs.pytest.org/)
- [pytest-cov](https://github.com/pytest-dev/pytest-cov)


## Project setup

Install `poetry`:
```
curl --silent --show-error --location https://install.python-poetry.org | python3 -
```

Create virtual environment by tool of your choice and activate it e.g.:
```
poetry shell
```

Install the project and its dependencies in a virtual environment:
```
poetry install
```


## Dev tools usage

Formating:
```
black .
```

Sorting imports:
```
isort .
```

Linting:
```
flake8p .
```

Type check:
```
mypy .
```


## Tests and coverage usage

To run tests:
```
pytest -v
```

To generate coverage report:
```
pytest --cov=turris_sentinel_network/
```


## Usage

To see how you can use it to implement a server infrastructure box see
[usage](./usage.md) and [examples](./examples/) folder.
