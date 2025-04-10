#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
poetry run streamlit run streamlit_app.py 