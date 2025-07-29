PROJECT := violetbeacon-deptrack-client

VENV := venv.nix
VENV_BIN := ${VENV}/bin
PIP := ${VENV_BIN}/pip
PYTHON := ${VENV_BIN}/python3

TESTPUBLISH_VENV := venv.nix.testpublish
TESTPUBLISH_PYTHON := ${TESTPUBLISH_VENV}/bin/python3

# Disable built-in make rules
MAKEFLAGS += --no-builtin-rules

.PHONY: setup
setup: mrclean
	python -m venv ${VENV}
	${PIP} install -U pip
	${PIP} install -r dev-requirements.txt
	uv python install 3.13 3.12 3.11 3.10 3.9

.PHONY: dev-setup
dev-setup: setup install-editable

.PHONY: install-editable
install-editable:
	${PIP} install --editable .

.PHONY: build
build: lint bom.json test
	tox -e build

.PHONY: clean
clean:
	rm -rf dist
	find src -type f -name "*.pyc" -exec rm -f {} \;
	find tests -type f -name "*.pyc" -exec rm -f {} \;
	rm -rf src/violetbeacon_deptrack_client.egg-info

.PHONY: mrclean
mrclean: clean
	rm -rf ${VENV}
	rm -rf .tox
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf htmlcov

bom.json: pyproject.toml
	tox run -e cyclonedx

.PHONY: cyclonedx-upload
cyclonedx-upload: VERSION := $(shell sed -n 's/^version\s*=\s*"\([^"]\+\)"$//\1/p' pyproject.toml)
cyclonedx-upload: bom.json
	deptrack-client upload-bom -p ${PROJECT} -q ${VERSION} -f bom.json

.PHONY: cicd
cicd: setup cyclonedx-upload tox-all

.PHONY: lint
lint:
	${VENV_BIN}/tox run-parallel -e lint,type

.PHONY: audit
audit:
	${VENV_BIN}/tox run -e audit

.PHONY: test
test:
	${VENV_BIN}/tox run -e coverage

.PHONY: test-all
test-all:
	${VENV_BIN}/tox run-parallel -e 3.13,3.12,3.10,3.9

.PHONY: tox-all
tox-all:
	tox run-parallel

.PHONY: publish-test
publish-test:
	${PYTHON} -m twine upload --repository testpypi dist/*

.PHONY: verify-publish-test
verify-publish-test:
	rm -rf ${TESTPUBLISH_VENV}
	python -m venv ${TESTPUBLISH_VENV}
	${TESTPUBLISH_PYTHON} -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ${PROJECT}
	${TESTPUBLISH_VENV}/bin/deptrack-client version

.PHONY: publish
publish:
	${VENV_PYTHON} -m twine upload dist/*

.PHONY: verify-publish
verify-publish:
	rm -rf ${TESTPUBLISH_VENV}
	python -m venv ${TESTPUBLISH_VENV}
	${TESTPUBLISH_PYTHON} -m pip install ${PROJECT}
	${TESTPUBLISH_VENV}/bin/deptrack-client version
