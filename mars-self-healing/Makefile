.PHONY: install test lint run-experiments plots ablation clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	ruff check src/ tests/
	mypy src/

run-experiments:
	python -m src.evaluation.fault_injector \
		--scenarios configs/scenarios/ \
		--output experiments/results/ \
		--runs 5

plots:
	python -m src.evaluation.metrics \
		--input experiments/results/ \
		--output experiments/plots/

ablation:
	python -m src.evaluation.fault_injector \
		--scenarios configs/scenarios/ \
		--ablation \
		--output experiments/results/ablation/

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov/ dist/ build/
	find . -type d -name __pycache__ -exec rm -rf {} +
