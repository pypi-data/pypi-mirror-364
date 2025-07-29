# pbs_monitoring_tools

This project provides tools that use Proxmox Backup Server (PBS) API with Proxmoxer, in order to get status informations, like backups that have failed.

## Get started

### Requirements

* python3 >= 3.11

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

To know how to use the `` package, please refer to [USAGE.md](USAGE.md) file.

## Tests

`test.py` is used to test project functions directly on a Proxmox Backup Server instance.

```shell
./test.py --auth-file <auth-file.yml>
```

But, in order to test some functions without to be authentificated to PBS, we use unit tests.

```shell
python3 -m unittest <path_to_file.py> # If you just need to test 1 file
python3 -m unittest discover <directory> # If you want to run all tests in a directory
```

## Formatting

We use **black** (for the version, please refer to [requirements.dev.txt](requirements.dev.txt) file) to format code, so before committing anything, don't forget to use:

```shell
black -l 120 <directory>
```
