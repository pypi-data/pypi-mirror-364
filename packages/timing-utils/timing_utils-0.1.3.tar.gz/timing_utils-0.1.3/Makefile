PACKAGE_NAME = timing_utils
PYPI_REPO = pypi
TESTPYPI_REPO = testpypi

.PHONY: help install test tox lint build publish test-publish clean uninstall

help:  ## Show help for each Makefile target
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z\/_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf " \033[36m%-20s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install dev dependencies into the current environment
	uv pip install -e .[dev]

test:  ## Run tests using pytest
	pytest

tox:  ## Run tests using tox (multiple Python versions)
	tox

lint:  ## Run linter using Ruff
	ruff check .

build:  ## Build the package
	rm -rf dist/
	python -m build

publish: build  ## Publish to PyPI
	twine upload --repository $(PYPI_REPO) dist/*

test-publish: build  ## Publish to TestPyPI
	twine upload --repository $(TESTPYPI_REPO) dist/*

clean:  ## Clean build and test artifacts
	rm -rf dist/ *.egg-info/ .pytest_cache/ .tox/ .coverage htmlcov/

uninstall:  ## Uninstall the package from the current environment
	pip uninstall -y $(PACKAGE_NAME)