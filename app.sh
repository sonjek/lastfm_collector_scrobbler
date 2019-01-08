#!/usr/bin/env bash

file=$(realpath "$0")
home=${file%/*}
exec "${home}/venv/bin/python" "${home}/app/app.py" "$@"
