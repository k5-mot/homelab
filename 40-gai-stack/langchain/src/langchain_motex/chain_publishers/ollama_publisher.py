#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from typing import Any, Dict, List

from langchain.globals import set_debug, set_verbose
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_ollama.chat_models import ChatOllama
from langchain_openai import AzureChatOpenAI
from ollama import Client
from pydantic import BaseModel

from langchain_motex.chain_publishers.base_publisher import BasePublisher

set_debug(False)
set_verbose(False)

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://homelab-ollama:11434")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-09-01-preview")

# Prompt Template
HUMAN_TEMPLATE = "{question}"




class OllamaPublisher(BasePublisher):
    def get_chain(self, model_name: str) -> Runnable:
        """A"""
        provider = "Ollama"
        path = re.sub(r"[ :\.\-]", "_", f"{provider}_{model_name}").lower()

        # Create basic components
        human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        prompt = ChatPromptTemplate.from_messages([human_prompt])
        llm = ChatOllama(base_url=OLLAMA_API_URL, model=model_name)
        parser = StrOutputParser()

        # Define the chain
        chain = RunnableParallel(
            {
                "answer": (
                    {"question": RunnablePassthrough()} | prompt | llm | parser
                ).with_types(input_type=Dict[str, str], output_type=str),
                "question": lambda x: x["question"],
            }
        )
        chain = chain.with_types(input_type=Dict[str, str], output_type=Dict[str, str])
        chain = chain.with_config(config=RunnableConfig(
            metadata={
                "title": f"{provider} - {model_name}",
                "provider": provider,
                "base_model": model_name,
                "collection": "",
                "docs_dir": "",
                "path": path,
                "content": f"- **Provider**: {provider}\n- **Model**: {model_name}",
            }
        ))

        return chain

    def get_chains(self):
        models = self.get_model_list()


        # Create chains based on the models
        chains = []
        for model in models:
            model_name = model["name"]
            chain = self.get_chain(model_name)


            chains.append({"chain": chain, "metadata": metadata})
        return chains

    def get_model_list(self):
        # Initialize Ollama client and get the model list
        client = Client(host=OLLAMA_API_URL)
        try:
            response = client.list()
            models = response.get("models", [])
            print(models)
        except Exception as e:
            print(f"Error: {e}")
            return []

def get_simple_llm_chains() -> List[Dict[str, Runnable | Dict[str, Any]]]:
    """Get simple LLM chains."""
    chains = [*get_ollama_chains()]  # , *get_azure_openai_chains()]
    return chains


def get_ollama_chains() -> List[Dict[str, Runnable | Dict[str, Any]]]:
    """Get simple LLM chains from Ollama."""

    # Initialize Ollama client and get the model list
    client = Client(host=OLLAMA_API_URL)
    try:
        response = client.list()
        models = response.get("models", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

    # Create chains based on the models
    chains = []
    for model in models:
        model_name = model["name"]

        # Create basic components
        human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        prompt = ChatPromptTemplate.from_messages([human_prompt])
        llm = ChatOllama(base_url=OLLAMA_API_URL, model=model_name)
        parser = StrOutputParser()

        # Define the chain
        chain = RunnableParallel(
            {
                "answer": (
                    {"question": RunnablePassthrough()} | prompt | llm | parser
                ).with_types(input_type=Dict[str, str], output_type=str),
                "question": lambda x: x["question"],
            }
        ).with_types(input_type=Dict[str, str], output_type=Dict[str, str])
        provider = "Ollama"
        path = re.sub(r"[ :\.\-]", "_", f"{provider}_{model_name}").lower()
        metadata = {
            "title": f"{provider} - {model_name}",
            "provider": provider,
            "base_model": model_name,
            "collection": "",
            "docs_dir": "",
            "path": path,
            "content": f"- **Provider**: {provider}\n- **Model**: {model_name}",
        }
        chains.append({"chain": chain, "metadata": metadata})
    return chains


def get_azure_openai_chains() -> List[Dict[str, Runnable | Dict[str, Any]]]:
    """Get simple LLM chains from Azure OpenAI."""

    model_names = ["gpt-3"]
    chains = []
    for model_name in model_names:
        # Create basic components
        human_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        prompt = ChatPromptTemplate.from_messages([human_prompt])
        llm = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            azure_deployment=model_name,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        parser = StrOutputParser()

        # Define the chain
        chain = RunnableParallel(
            {
                "answer": (
                    {"question": RunnablePassthrough()} | prompt | llm | parser
                ).with_types(input_type=Dict[str, str], output_type=str),
                "question": lambda x: x["question"],
            }
        ).with_types(input_type=Dict[str, str], output_type=Dict[str, str])
        provider = "Azure OpenAI"
        path = re.sub(r"[ :\.\-]", "_", f"{provider}_{model_name}").lower()
        metadata = {
            "title": f"{provider} - {model_name}",
            "provider": provider,
            "base_model": model_name,
            "collection": "",
            "docs_dir": "",
            "path": path,
            "content": f"- **Provider**: {provider}\n- **Model**: {model_name}",
        }
        chains.append({"chain": chain, "metadata": metadata})

    return chains


if __name__ == "__main__":
    publisher = OllamaPublisher()
    chain = publisher.get_chain()
    # chains = get_simple_llm_chains()
    # print("LLMChains")
    # for chain_with_metadata in chains:
    #     chain = chain_with_metadata["chain"]
    #     metadata = chain_with_metadata["metadata"]
    #     print(metadata["path"])
