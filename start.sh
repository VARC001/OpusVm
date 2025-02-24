#!/bin/bash

set -e

gunicorn -w 4 -b 0.0.0.0:${PORT:-8080} Vortex:create_app &

python3 -m Opus
