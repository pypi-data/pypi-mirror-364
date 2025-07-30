test *opts:
    pytest tests {{ opts }}

format:
    ruff format .
    ruff check . --fix

lint:
    ruff format --check .
    ruff check .
    mypy .
