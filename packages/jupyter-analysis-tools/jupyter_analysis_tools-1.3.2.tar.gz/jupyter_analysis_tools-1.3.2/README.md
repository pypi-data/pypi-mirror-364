# Overview

Yet another Python library with helpers and utilities for data analysis and processing.

[![PyPI Package latest release](https://img.shields.io/pypi/v/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools)
[![Commits since latest release](https://img.shields.io/github/commits-since/BAMresearch/jupyter-analysis-tools/v1.3.2.svg)](https://github.com/BAMresearch/jupyter-analysis-tools/compare/v1.3.1...main)
[![License](https://img.shields.io/pypi/l/jupyter-analysis-tools.svg)](https://en.wikipedia.org/wiki/MIT_license)
[![Supported versions](https://img.shields.io/pypi/pyversions/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools#files)
[![Weekly PyPI downloads](https://img.shields.io/pypi/dw/jupyter-analysis-tools.svg)](https://pypi.org/project/jupyter-analysis-tools/)
[![Continuous Integration and Deployment Status](https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/BAMresearch/jupyter-analysis-tools/actions/workflows/ci-cd.yml)
[![Coverage report](https://img.shields.io/endpoint?url=https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/cov.json)](https://BAMresearch.github.io/jupyter-analysis-tools/coverage-report/)

## Installation

    pip install jupyter-analysis-tools

You can also install the in-development version with:

    pip install git+https://github.com/BAMresearch/jupyter-analysis-tools.git@main

## Documentation

https://BAMresearch.github.io/jupyter-analysis-tools

## Development

Run all tests with:

    tox -e py

Note, to combine the coverage data from all the tox environments run:

- Windows

        set PYTEST_ADDOPTS=--cov-append tox

- Other

        PYTEST_ADDOPTS=--cov-append tox
