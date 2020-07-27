# Watchtower

This is the userspace Sentinel component that samples the hardware data exposed by the [Sentinel Kernel Module](https://github.com/AdrienCos/sentinel). 


# Configuration
The configuration is stored in the `config.py` file. The available parameters are:



## Installation

* Create a new virtual environment: `virtualenv venv`
* Activate it: `source venv/bin/activate`
* Install the dependencies: `pip install -e .`


### Installing Postgres on a Raspberry Pi

```
sudo apt install postgresql libpq-dev
sudo su postgres
createuser pi -P --interactive
psql
create database sentinel;
```


## Usage

Watchtower is composed of two application: one runs on the nodes, and one runs on the hub.

It imports the `config_node/hub.py` file to get its configuration. These configuration files contain le list of all the files exposed by the SKM, in the following format: 

`files`: list of dictionaries, each entry corresponds to a file that should be sampled. The format of the `dict` is as follow:
  * `path` (`str`): absolute path to the file to read
  * `name` (`str`): name of the corresponding header column
  * `unit` (`str`): unit of the value
  * `differential` (`bool`): whether the measurement should be substracted to the previous one (e.g. network traffic)


**Note:** This is not very practical, as any change made to the SKM needs to be reflected in every instance of Watchtower. Ideally, some dynamic solution would be implemented in the future, where the nodes can enumerate the files, report to the hub, and be told which ones to report

To run the node side: `python main_node.py`. Watchtower will connect to the MQTT broker, and start polling all the files periodically and reporting their contents. 

To run the hub side: `python main_hub.py`. Watchtower will connect to the MQTT broker, and subscribe to the `nodes/` topic. As the nodes advertise themselves on this topic, the hub then subscribes to their individual topics. This allows the list of nodes to be fully dynamic, as the hub can learn about them at any time.

### Drill-down / Backoff

The nodes default to reporting their data at a rate defined in their config file. This rate can however be dynamically changed. The file `backoff.py` presents an example of how this can be performed.

### Resetting the Postgres database

If you want to erase the contents of the Postgres database (because you want to start a new experiemntal run for instance), use the `reset_db.sh` bash script. 

**CAUTION:** this will permanently erase the contents of the `sentinel` database wihtout asking confirmation. Make sure you have saved all important data beforehand.