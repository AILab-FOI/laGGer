#!/usr/bin/env bash

echo "Starting game streaming agent"

screen -S laGGerGame -d -m ./game_streaming_agent.py

echo "Starting video streaming agent"

screen -S laGGerVideo -d -m ./video_streaming_agent.py

echo "If there were no errors above you can connect to the laGGer game streaming agent with:"

echo ""

echo "screen -r laGGerGame"

echo ""

echo "And to the laGGer video streaming agent with:"

echo ""

echo "screen -r laGGerVideo"

echo ""

echo "To exit the session, without killing the program use CTRL+a CTRL+d"

echo ""
