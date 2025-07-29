#!/bin/bash

# Run ruff linter with auto-fix
ruff check jup_python_sdk tests --fix

# Run ruff formatter
ruff format jup_python_sdk tests

# Run mypy for type checking
mypy jup_python_sdk tests

# Run tests
pytest