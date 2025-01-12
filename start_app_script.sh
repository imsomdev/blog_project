#!/bin/bash
cd /home/ubuntu/blog_project
source venv/bin/activate
uvicorn blog_project.asgi:application --host 0.0.0.0 --port 8000 --workers 4 --log-level debug
