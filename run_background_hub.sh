#/bin/bash

screen -S watchtower_hub -d -m pipenv run python $HOME/src/watchtower/main_hub.py
