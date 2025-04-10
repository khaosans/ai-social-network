#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
poetry run uvicorn main:app --port 8000 --reload 