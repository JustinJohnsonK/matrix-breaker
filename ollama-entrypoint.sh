#!/bin/sh
set -e
ollama serve &
sleep 2
ollama pull phi3 || true
wait $!
