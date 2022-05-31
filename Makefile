
help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "[36m%-30s[0m %s\n", $$1, $$2}'

# Local installation
.PHONY: init clean lock update install

install: ## Initalise the virtual env installing deps
	pipenv install --dev

clean: ## Remove all the unwanted clutter
	find src -type d -name __pycache__ | xargs rm -rf
	find src -type d -name '*.egg-info' | xargs rm -rf
	pipenv clean
	rm -rf build
	rm -rf dist

lock: ## Lock dependencies
	pipenv lock

update: ## Update dependencies (whole tree)
	pipenv update --dev

sync: ## Install dependencies as per the lock file
	pipenv sync --dev

# Linting and formatting
.PHONY: lint format

lint: ## Lint files with flake and mypy
	pipenv run flake8 src  tests  functional
	pipenv run mypy src  tests  functional
	pipenv run black --check src  tests  functional
	pipenv run isort --check-only src  tests  functional

format: ## Run black and isort
	pipenv run black src  tests  functional
	pipenv run isort src  tests  functional

# Testing

.PHONY: test functional
test: ## Run unit tests
	TZ=UTC pipenv run pytest tests

functional: ## Run functional tests
	TZ=UTC pipenv run pytest functional 
