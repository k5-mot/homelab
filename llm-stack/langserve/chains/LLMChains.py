import os
from typing import List
from ollama import Client
from langchain_core.runnables import Runnable
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import AzureOpenAI


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://homelab-ollama:11434")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-09-01-preview")


def getLLMChains() -> List[Runnable]:
    chains = []
    chains.extend(getOllamaChains())
    # chains.extend(getOpenAIChains())
    return chains


def getOllamaChains() -> List[Runnable]:
    # Get model list
    client = Client(host=OLLAMA_API_URL)
    response = client.list()

    # Get Ollama chains
    chains = [
        ChatOllama(base_url=OLLAMA_API_URL, model=model["name"], name=model["name"])
        for model in response["models"]
    ]
    return chains


def getOpenAIChains() -> List[Runnable]:
    # Get Azure OpenAI chains
    chains = [
        AzureOpenAI(
            name="gpt-3",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=1.0,
        ),
    ]
    return chains


if __name__ == "__main__":
    chains = getLLMChains()
    print(chains)
