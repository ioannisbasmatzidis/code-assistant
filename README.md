# Code Assistant

## Summary

The code assistant service is a chat interface for a developer crew that helps POs and engineers write, test, and evaluate code.


## Install

### Configure Poetry

Make sure you have the `poetry` installed and configured properly:

1. Install poetry:

   `curl -sSL https://install.python-poetry.org | python3 -`



#### Install project venv and dependencies

```bash
poetry install
```


#### Use make

Run `make` to see your options.


The Makefile in this project contains convenience scripts to help your day to day coding. See below:


Formatting and verification (isort, black, mypy, pylint):

```bash
make fmt
```

Run tests:

```bash
make test
```
