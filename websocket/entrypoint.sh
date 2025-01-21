#!/bin/sh

exec uvicorn main:application --host 0.0.0.0 --port $WEBSOCKET_INTERNAL_PORT
