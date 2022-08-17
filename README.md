# Sentinel Python project template

This is a sample Python project for Turris Sentinel - threat detection and cyberattack
prevention system. Its purpose is to define Python project structure and related
tools and their configuration.

To see how to start a new project from it or to incorporate it to an existing
project see project
[wiki](https://gitlab.nic.cz/turris/sentinel/sentinel-python-project-template/-/wikis/home)
in our Gitlab. You can find there comments on various aspects of a project
(structure, package/dependency distribution, CI,...) as well.


## Dependencies

- [sn](https://gitlab.nic.cz/turris/sentinel/sn) - our internal Sentinel Network library

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


## Example usage

To run `template_box`:
```
template_box \
	--resource in,bind,PULL,127.0.0.1,9000 \
	--resource out,connect,PUSH,127.0.0.1,9090
```

To run `dev` boxes (input generator and output dumper):
```
./dev/dumper.py --resource "in,bind,PULL,127.0.0.1,9090"
./dev/feeder.py --resource "out,connect,PUSH,127.0.0.1,9000"
```

You can pass `--help` otption to all the above comands for more information
how to use them.


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
pytest --cov=turris_sentinel_template_box/
```
