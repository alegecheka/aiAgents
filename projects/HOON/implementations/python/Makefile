test:
	@echo "Running Pytest..."
	PYTHONPATH=src pytest tests/
	@echo "\nRunning Universal CLI Bash tests..."
	PYTHONPATH=src ./tests/run-tests.sh

clean:
	rm -rf .pytest_cache build dist src/hoon.egg-info src/hoon/__pycache__ tests/__pycache__

.PHONY: test clean
