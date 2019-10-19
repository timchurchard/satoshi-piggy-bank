#!/bin/bash

if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ ! -f "./venv/bin/activate" ]; then
        # Install virtualenv
        python3 -m venv venv
        . venv/bin/activate
        pip3 install -U pip setuptools
        pip3 install -r requirements.txt
        pip3 install -r requirements-test.txt
    fi
fi

export INCLUDES="code/piggy-bank"
export PYTHONPATH="code"

. venv/bin/activate
flake8 --config flake8.cfg $INCLUDES
pylint --rcfile pylint.rc $INCLUDES
deactivate
