format:
	black .

format.diff:
	black . --diff --color

test:
	python -m pytest 

test.unit:
	python -m pytest -m "not integration"

test.integration:
	python -m pytest -m "integration"
