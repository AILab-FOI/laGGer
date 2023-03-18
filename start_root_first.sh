#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root!" 
   exit 1
fi

echo "Starting Janus"

export LD_LIBRARY_PATH=/usr/lib && screen -S Janus -d -m /opt/janus/bin/janus -d 5

echo "Staring registration agent"

screen -S laGGerRegister -d -m ./register_user_service.py

echo "If there were no errors above you can connect to the Janus server with:"

echo ""

echo "screen -r Janus"

echo ""

echo "And to the laGGer registration agent with:"

echo ""

echo "screen -r laGGerRegister"

echo ""

echo "To exit the session, without killing the program use CTRL+a CTRL+d"

echo ""
