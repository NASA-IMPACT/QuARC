# QuARC: PyQuARC as a service

[PyQuARC](https://github.com/NASA-IMPACT/pyquarc) is an open source library for Earth Observation metadata quality assessment.

Learn more in the linked [Github repo](https://github.com/NASA-IMPACT/pyquarc).

QuARC is a service built on top of pyQuARC to provide easily accessible metadata quality assessment.

# Code Formatting and Linting
This project enforces linting and formatting upon pull requests via Github Actions. Formatter and linter config files are included in the repo, and users are encouraged to enable auto-formatting in their code editor, which should automatically use the included configs.

Necessary Python libraries can be installed with `requirements_dev.txt`.

For further details on team coding standards which are not automatically checked by Github Actions, please read the [conventions document](https://docs.google.com/document/d/1b0YSCObQu3yvWeblHDDeIKzapxUkuVQVElGw_rxrC4Q/view).
## Python
For python, this project uses [Black](https://black.readthedocs.io/en/stable/) for formatting and [Flake8](https://flake8.pycqa.org/en/latest/) for linting. Configurations are in the following locations:
  - [Black configuration](pyproject.toml)
  - [Flake8 configuration](tox.ini)
  - [Github action](.github/workflows/lint.yml) for linting and formatting check