#!/bin/sh

exec uvicorn main:application --host 0.0.0.0 --port $VOICE_INTERNAL_PORT
