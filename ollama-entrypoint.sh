#!/bin/sh
set -e
ollama serve &
sleep 2
ollama pull mistral:instruct || true
wait $!
