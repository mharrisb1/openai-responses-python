# Contributing

All contributions are welcome.

## Development Environment

This project uses [Poetry](https://python-poetry.org/) to manage Python environment, [Black](https://github.com/psf/black) to format code,
and [mypy](https://mypy-lang.org/) to run static analysis. Please make sure your environment is setup with these enabled.

To make sure everything is working correctly, make sure you have Poetry installed, then install the dependencies, and then run [tox](https://tox.wiki/en/4.14.2/).

```sh
pipx install poetry==1.8 --force
poetry config virtualenvs.in-project true
poetry install --with dev
poetry shell
tox run
```
