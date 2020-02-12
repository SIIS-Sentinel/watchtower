#/bin/bash

screen -S watchtower_node -d -m pipenv run python $HOME/src/watchtower/main_node.py
