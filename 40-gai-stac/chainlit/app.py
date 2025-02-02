import os, requests, random
from typing import List, Dict, Any
import chainlit as cl
from langchain_core.documents import Document

from langserve import RemoteRunnable
from langchain_core.runnables import Runnable, RunnableConfig


# Get LangServe API list
LANGSERVE_BASE_URL = "http://homelab-langserve:8000"
# LANGSERVE_BASE_URL = "http://localhost:8001"
LANGSERVE_LIST_URL = f"{LANGSERVE_BASE_URL}/list"
response = requests.get(LANGSERVE_LIST_URL).json()
chains = response["chains"]
for chain in chains:
    print(chain["path"])
    chain["runnable"] = RemoteRunnable(url=f"{LANGSERVE_BASE_URL}/{chain["path"]}")


def get_chain(chains: List[Dict[str, Any]], chat_profile: str) -> Dict[str, Any]:
    """Get chain"""
    return next((chain for chain in chains if chain["title"] == chat_profile), None)


@cl.set_chat_profiles
async def chat_profiles(current_user: cl.User):
    """Set chat profiles."""

    # Create chat profiles
    profiles: List[cl.ChatProfile] = []
    for chain in chains:
        seed = "{:0>6}".format(random.randint(0, 999999))
        profiles.append(
            cl.ChatProfile(
                name=chain["title"],
                markdown_description=chain["content"],
                icon=f"https://picsum.photos/seed/{seed}/200",
            )
        )

    # Set default chat profile
    for profile in profiles:
        if "RAG" in profile.name:
            profile.default = True
            break
    return profiles


@cl.on_chat_start
async def on_chat_start():
    """Event on chat start."""
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    chain = get_chain(chains, chat_profile)
    # chain = next((chain for chain in chains if chain["title"] == chat_profile), None)
    await cl.Message(content=f"{chain["content"]}").send()


@cl.on_message
async def on_message(message: cl.Message):
    reply = cl.Message(content="", elements=[])
    chat_profile = cl.user_session.get("chat_profile")

    # Get chains
    # chain = next((chain for chain in chains if chain["title"] == chat_profile), None)
    chain = get_chain(chains, chat_profile)
    runnable = chain["runnable"]

    # Stream messages
    contexts = []
    for chunk in runnable.stream(
        input={"question": message.content},
        config=RunnableConfig(
            callbacks=[cl.LangchainCallbackHandler(stream_final_answer=True)]
        ),
    ):
        if "answer" in chunk.keys():
            await reply.stream_token(chunk["answer"])
        elif "context" in chunk.keys():
            contexts.extend(chunk["context"])
        elif "question" in chunk.keys():
            question = chunk["question"]
        elif "prompt" in chunk.keys():
            prompt = chunk["prompt"]
    await reply.send()

    # Set contexts to elements of a message
    for context in contexts:
        # Skip added documents
        print(context)
        file_path = os.path.abspath(context["file_path"])

        # Create new element
        reply.elements.append(
            cl.Text(
                name=file_path,
                # language=context.metadata["file_type"],
                content=context["content"],
                # path=context_path
            )
        )
    await reply.send()

    # await cl.Message(content=f"Q. {question}", elements=[]).send()
    # prompt = [
    #     message.content
    #     for message in prompt["messages"]
    #     if type(message) is HumanMessage
    # ][0]
    # await cl.Message(content=f"P. {prompt}", elements=[]).send()
