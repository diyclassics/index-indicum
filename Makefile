init:
	    pip install pipenv
	    pipenv install --dev
			pip install -e .

test:
	    pipenv run py.test tests
