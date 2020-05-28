# Watchtower

This is the userspace application that samples the hardware data exposed by the Linux Kernel Module [Sentinel](https://github.com/AdrienCos/sentinel). 

# Configuration
The configuration is stored in the `config.py` file. The available parameters are:

* `sample_period`: delay between two samples, in seconds
* `csv_path`: path to the CSV file where Watchtower store its output
* `files`: list of dictionaries, each entry corresponds to a file that should be sampled. The format of the `dict` is as follow:
  * `path`: absolute path to the file to read
  * `name`: name of the corresponding header column
  * `unit`: unit of the value
  * `differential`: whether the measurement should be substracted to the previous one (e.g. network traffic)

## Example of `files` entry


    {"path": "/path/to/file",
        "name": "Example value",
        "unit": "kB",
        "differential": 0
    }


## Setup on a new machine

* Clone this repo
* Install `pip3`, `virtualenv`, create a virtualenv for this repo, and install all the dependencies

```
sudo apt install python3-pip
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
* Install Postgres, create a new user `pi` and a `sentinel` database

```
sudo apt install postgresql libpq-dev
sudo su postgres
createuser pi -P --interactive
psql
create database sentinel;
```
