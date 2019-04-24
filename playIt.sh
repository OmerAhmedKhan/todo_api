#!/bin/bash

sudo apt install virtualenv
mkdir /home/$USER/virtual_env
cd /home/$USER/virtual_env/
virtualenv -p python3 hem_test
. hem_test/bin/activate
cd /home/$USER/HemTest/
python3 setup.py install
python3 api.py
