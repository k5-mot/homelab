#!/usr/bin/env bash

# Summary:
# Setup LLM models included in the library

# Clear a part of proxy
export http_proxy=
export HTTP_PROXY=

# Run the server temporarily
ollama serve &

# Pull LLM models
ollama pull llama3.1:8b
ollama pull gemma2:9b
ollama pull codegemma:7b
ollama pull deepseek-coder-v2:16b
ollama pull nomic-embed-text:latest
