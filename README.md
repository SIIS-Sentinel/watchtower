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
