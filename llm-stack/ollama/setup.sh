#!/usr/bin/env bash

cd /root/ollama
model_dir="/root/ollama/model"

# Setup
apt-get update
# apt-get upgrade -y
# apt-get autoremove -y
apt-get install -y wget

export http_proxy=
export HTTP_PROXY=

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
if [ ! -e ${model_dir}/elyza3/*.gguf ]; then
    echo "Download elyza3:8b"
    wget -P ${model_dir}/elyza3 https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-GGUF/resolve/main/Llama-3-ELYZA-JP-8B-q4_k_m.gguf
fi
ollama create elyza3:8b -f ${model_dir}/elyza3/Modelfile

if [ ! -e ${model_dir}/llm-jp/*.gguf ]; then
    echo "Download llm-jp:13b"
    wget -P ${model_dir}/llm-jp https://huggingface.co/mmnga/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-gguf/resolve/main/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-Q4_K_M.gguf
fi
ollama create llm-jp:13b -f ${model_dir}/llm-jp/Modelfile

if [ ! -e ${model_dir}/watashiha/*.gguf ]; then
    echo "Download watashiha:6b"
    wget -P ${model_dir}/watashiha https://huggingface.co/mmnga/watashiha-gpt-6b-gguf/resolve/main/watashiha-gpt-6b-q4_K_M.gguf
fi
ollama create watashiha:6b -f ${model_dir}/watashiha/Modelfile
