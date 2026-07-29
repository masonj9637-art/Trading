#!/bin/bash
# Start the FastAPI inference server in the foreground
exec uvicorn inference.main:app --host 0.0.0.0 --port 8000
