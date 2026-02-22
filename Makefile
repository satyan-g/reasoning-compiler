.PHONY: setup test clean

setup:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
