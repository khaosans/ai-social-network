#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)/..

# Kill any existing processes
pkill -f "uvicorn.*webhook:app" || true
pkill -f "python.*agent_manager.py" || true

# Start the webhook server in the background
poetry run uvicorn webhook:app --port 9000 --reload &

# Wait for the webhook server to start
sleep 2

# Start the agent manager
poetry run python agent_manager.py 