# Development

A Makefile exists to set up the environment and run common dev and build-related commands.

[Tox](https://tox.wiki) is used for tests, coverage reports, linting, etc.  The tox configuration is in `pyproject.toml`.

Python versions are managed using [uv](https://docs.astral.sh/uv/). Ensure UV is installed before running the setup step.

## Security Issues

If you find a security issue, please email security at vltbcn.com and include as much detail as possible. Please do not raise it as an issue here. Thanks!

## Setup

Create the virtual environment, install dependencies, and install the project in editable mode.

```bash
$ make dev-setup
```

## Run tests

```bash
$ make test
```

## Run lint

```bash
$ make lint
```

## Run tests against all versions of Python

```bash
$ make test-all
```

## Generate bom.json

```bash
$ make bom.json
```

## Upload bom.json

```bash
# 1. Set DTRACK_BASEURL to your Dependency-Track instance URL
# 2. Set DTRACK_APIKEY to your Dependency-Track API key
$ make cyclonedx-upload
```

## Build and publish a release

```bash
$ make build
$ make publish-build
```
