#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = streaming-data-project
REGION = eu-west-2
PYTHON_INTERPRETER = python
WD=$(shell pwd)
PYTHONPATH=${WD}/src
SHELL := /bin/bash
PROFILE = default
PIP:=pip

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON_INTERPRETER) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PIP) install -q virtualenv virtualenvwrapper; \
	    virtualenv venv --python=$(PYTHON_INTERPRETER); \
	)

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)


## Add new environment requirements
add-requirements: 
	$(call execute_in_env, $(PIP) freeze > ./requirements.txt)

################################################################################################################
# Build / Run

## Run the security test (bandit + safety)
security-test:
	$(call execute_in_env, safety check -r ./requirements.txt -i 70612)
	$(call execute_in_env, bandit -lll */*.py *c/*/*.py)

## Run the flake8 code check
run-flake:
	$(call execute_in_env, flake8  ./src/*/*.py ./test/*/*.py)

## Run the unit tests
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest -rP ./test/test_input_tool)
	$(call execute_in_env, PYTHONPATH=${WD}/src/ingestion_lambda pytest -rP ./test/test_ingestion_functions/)
	$(call execute_in_env, PYTHONPATH=${WD}/src/transformation_lambda pytest -rP ./test/test_transformation_functions/)
	$(call execute_in_env, PYTHONPATH=${WD}/src/loading_lambda pytest -rP ./test/test_loading_functions/)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} coverage run --omit 'venv/*' -m pytest ./test/test_input_tool && coverage report -m)
	$(call execute_in_env, PYTHONPATH=${WD}/src/ingestion_lambda coverage run --omit 'venv/*' -m pytest ./test/test_ingestion_functions/ && coverage report -m)
	$(call execute_in_env, PYTHONPATH=${WD}/src/transformation_lambda coverage run --omit 'venv/*' -m pytest ./test/test_transformation_functions/ && coverage report -m)
	$(call execute_in_env, PYTHONPATH=${WD}/src/loading_lambda coverage run --omit 'venv/*' -m pytest ./test/test_loading_functions/ && coverage report -m)

## Run all checks
run-checks: security-test run-flake unit-test check-coverage

################################################################################################################
## Run the application (CLI)
create-new-search:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} python src/input_tool/create_new_search.py)