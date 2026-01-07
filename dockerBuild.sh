#!/bin/bash
set -e

IMAGE_NAME=sp500_db

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "Mac détecté → build en linux/amd64"
  docker buildx build --platform linux/amd64 -t $IMAGE_NAME .
else
  echo "Linux détecté → build standard"
  docker build -t $IMAGE_NAME .
fi