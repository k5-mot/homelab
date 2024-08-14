#!/usr/bin/env bash

cd /root

# Setup
# apt update
# apt upgrade -y
# apt autoremove -y
apt install -y wget

# Pull LLM models
ollama pull llama3.1:8b
# ollama pull llama3.1:70b
# ollama pull llama3.1:405b
ollama pull deepseek-coder-v2:16b
# ollama pull deepseek-coder-v2:236b
# ollama pull deepseek-coder:1.3b
# ollama pull deepseek-coder:6.7b
# ollama pull deepseek-coder:33b
ollama pull nomic-embed-text:latest
# ollama pull llava:7b

# Pull LLM models without library
if [ ! -e ./ollama/elyza3/*.gguf ]; then
    echo "Download elyza3:8b"
    wget -P ./ollama/elyza3 https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-GGUF/resolve/main/Llama-3-ELYZA-JP-8B-q4_k_m.gguf
fi
ollama create elyza3:8b -f ./ollama/elyza3/Modelfile

if [ ! -e ./ollama/llm-jp/*.gguf ]; then
    echo "Download llm-jp:13b"
    wget -P ./ollama/llm-jp https://huggingface.co/mmnga/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-gguf/resolve/main/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-Q4_K_M.gguf
fi
ollama create llm-jp:13b -f ./ollama/llm-jp/Modelfile

if [ ! -e ./ollama/watashiha/*.gguf ]; then
    echo "Download watashiha:6b"
    wget -P ./ollama/watashiha https://huggingface.co/mmnga/watashiha-gpt-6b-gguf/resolve/main/watashiha-gpt-6b-q4_K_M.gguf
fi
ollama create watashiha:6b -f ./ollama/watashiha/Modelfile
