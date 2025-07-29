# changelog-tools

This project provides tools to manage changelog files, according to the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

## Get started

### Requirements

* python3 >= 3.8

```shell
apt install python3 python3-pip python3-venv
```

Create a virtual env:

```shell
python3 -m venv venv
source venv/bin/activate
```

Then, install the requirements:

```shell
pip3 install -r requirements.dev.txt
```

## Usage

```shell
cd src/
```
For development purpose, go to the `/src` directory to be able to use and test package.

To know how to use the `changelog_tools` package, please refer to [USAGE.md](USAGE.md) file.

## Tests

### Unit tests

To run the unit tests, you need to use this command line:

```shell
python3 -m unittest <file.py> # Run a specific test file
python3 -m unittest discover <directory> # Run all tests files from a specific directory
```

### Integration tests

To run integration tests, you need to use this command line:

```shell
./tests/integration_tests/test_app.sh
```

## Formatting

We use **black** (for the version, please refer to `requirements.dev.txt` file) to format code, so before committing anything, don't forget to use:

```
black -l 120 <directory>
```
