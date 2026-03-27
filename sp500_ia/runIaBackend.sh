#!/bin/bash

echo "Install main dependencies :"
echo "pip install fastapi uvicorn requests"

echo "Install deepseek ai :"
echo "curl -fsSL https://ollama.com/install.sh | sh"
echo "ollama pull deepseek-r1"

echo "Lancer le back :"
echo "ollama run deepseek-r1"
echo "uvicorn main:app --reload --port 8001"