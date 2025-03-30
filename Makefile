PROJECT_NAME=code_assistant

.DEFAULT: help

.PHONY: fmt style verify test run test-cov clean
help:
	@echo ""
	@echo "$(BOLD)$(PROJECT_NAME)$(RESET)"
	@echo "======"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""

fmt:  ## Format code using lint
	poetry run ./scripts/lint.sh --fix --p SERVICE -t --name code_assistant

style:  ## Run linting checks
	poetry run ./scripts/lint.sh --p SERVICE -t --name code_assistant

verify: style test  ## Run all checks and tests

test:  ## Run tests
	poetry run pytest

test-cov:  ## Run tests with coverage
	poetry run pytest --cov=code_assistant --cov-report=term-missing

run:  ## Run the Streamlit app
	poetry run streamlit run code_assistant/app/app.py 

clean:  ## Clean up the project
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	rm -rf .coverage coverage_html_report .pytest_cache .mypy_cache build dist
