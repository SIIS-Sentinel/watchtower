#/bin/bash

source venv/bin/activate
screen -S watchtower_hub -d -m python ./main_hub.py
