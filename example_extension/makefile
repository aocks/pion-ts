
# Simple makefile to help manage the project

.PHONY: pypi help test_pypi clean check test lint

# The stuff below implements an auto help feature
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:   ## Show help for avaiable targets
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint:   ## Run linter on project
	PYTHONPATH=../src:${PYTHONPATH} pylint src

test:   ## Run tests
	PYTHONPATH=../src:src py.test -s -vvv \
            --doctest-modules --doctest-glob='*.md' .

check:  ## Run linting, tests, etc.
	${MAKE} lint
	${MAKE} test


clean:  ## Clean out generated files.
	\rm -rf dist *.egg-info src/*.egg-info

test_pypi:  check dist  ## Test pypi upload
	python3 -m twine upload --verbose --repository testpypi dist/*

pypi:   check dist  ## Upload to pypi
	python3 -m twine upload --verbose dist/*

dist:   ## Build distribution
	python3 -m build 


update:  ## Install/update tools required for packaging
	pip install --upgrade setuptools wheel twine build packaging
