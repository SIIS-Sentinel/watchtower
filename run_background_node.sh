#/bin/bash

source venv/bin/activate
screen -S watchtower_node -d -m python ./main_node.py
