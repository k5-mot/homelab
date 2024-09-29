#!/usr/bin/env bash

# Summary:
# Setup LLM models NOT included in the library

# Go to build dir
cd /workspace
model_dir="/workspace/model"

# Clear a part of proxy
export http_proxy=
export HTTP_PROXY=

# Run the server temporarily
ollama serve &

# Download LLM models in parallel
cd ${model_dir}/elyza3
curl -LO https://huggingface.co/elyza/Llama-3-ELYZA-JP-8B-GGUF/resolve/main/Llama-3-ELYZA-JP-8B-q4_k_m.gguf
cd ${model_dir}/llm-jp
curl -LO https://huggingface.co/mmnga/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-gguf/resolve/main/llm-jp-13b-instruct-full-ac_001_16x-dolly-ichikara_004_001_single-oasst-oasst2-v2.0-Q4_K_M.gguf
cd ${model_dir}/watashiha
curl -LO https://huggingface.co/mmnga/watashiha-gpt-6b-gguf/resolve/main/watashiha-gpt-6b-q4_K_M.gguf

# Create LLM models
ollama create elyza3:8b    -f ${model_dir}/elyza3/Modelfile
ollama create llmjp-v2:13b -f ${model_dir}/llm-jp/Modelfile
ollama create watashiha:6b -f ${model_dir}/watashiha/Modelfile
