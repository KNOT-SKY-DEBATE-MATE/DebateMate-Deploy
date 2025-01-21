#!/bin/bash

exec uvicorn main:application --host 0.0.0.0 --port $ANNOTATOR_INTERNAL_PORT