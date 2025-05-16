#!/usr/bin/env bash
pip install -r requirements.txt
export PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium 