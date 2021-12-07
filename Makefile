help:
	echo "Run 'make test' to test or 'make pip' to install requirements"

test: pytest_test linting_test

pip: pip_upgrade pip_requirements

pip_upgrade:
	python -m pip install --upgrade pip

pip_requirements:
	python -m pip install -r requirements.txt
	python -m pip install -r requirements-dev.txt

pytest_test:
	pytest --html=reports/unittests.html --self-contained-html --cov=git_web --cov-report html:reports/coverage tests/

linting_test:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

radon_cc:
	radon cc git_web -a -nc
