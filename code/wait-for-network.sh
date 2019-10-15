#!/bin/bash
echo "Waiting for network..."
HOST="8.8.8.81"
TIMEOUT=30
tries=1
while ! ping -c 1 -W 1 $HOST >/dev/null 2>&1 ; do
    if [ $tries -gt $TIMEOUT ]; then
        echo "No network!"
        exit 1
    fi
    echo "Waiting for $HOST - network interface might be down..."
    sleep 2
    ((tries++))
done
echo "Found network"
