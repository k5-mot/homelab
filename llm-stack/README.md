# Homelab LLM Stack

## :scroll: Setup

```bash
cd ./llm-stack
sudo docker compose up -d
sudo docker exec -it homelab-ollama /bin/bash -c "sh /root/ollama/setup.sh"
```

## VSCode Continue拡張機能のおすすめ設定

```json
{
    "models": [
        {
            "title": "Ollama",
            "provider": "ollama",
            "model": "AUTODETECT",
            "apiBase": "http://localhost:30100/"
        }
    ],
    "tabAutocompleteModel": {
        "title": "deepseek-coder-v2:16b",
        "provider": "ollama",
        "model": "deepseek-coder-v2:16b",
        "apiBase": "http://localhost:30100/"
    },
    "embeddingsProvider": {
        "provider": "ollama",
        "model": "nomic-embed-text",
        "apiBase": "http://localhost:30100/"
    },
    "allowAnonymousTelemetry": true
}
```
