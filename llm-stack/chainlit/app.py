import os
from typing import List
import chainlit as cl
from langchain_core.documents import Document
from langserve import RemoteRunnable
from langchain.schema.runnable.config import RunnableConfig

base_url = "http://homelab-langserve:8000"
# base_url = "http://localhost:8001"
chains = [
    {"name": "codegemma_7b", "chain": RemoteRunnable(f"{base_url}/codegemma_7b")},
    {"name": "gemma2_9b", "chain": RemoteRunnable(f"{base_url}/gemma2_9b")},
    {"name": "watashiha_6b", "chain": RemoteRunnable(f"{base_url}/watashiha_6b")},
    {"name": "llmjp_v2_13b", "chain": RemoteRunnable(f"{base_url}/llmjp_v2_13b")},
    {"name": "elyza3_8b", "chain": RemoteRunnable(f"{base_url}/elyza3_8b")},
    {
        "name": "deepseek_coder_v2_16b",
        "chain": RemoteRunnable(f"{base_url}/deepseek_coder_v2_16b"),
    },
    {"name": "llama3_2_3b", "chain": RemoteRunnable(f"{base_url}/llama3_2_3b")},
    {"name": "rag_sample", "chain": RemoteRunnable(f"{base_url}/rag_sample")},
    {"name": "rag_sample2", "chain": RemoteRunnable(f"{base_url}/rag_sample2")},
]


@cl.set_chat_profiles
async def chat_profiles(current_user: cl.User):
    profiles = [
        cl.ChatProfile(
            name=chain["name"],
            markdown_description="",
            # icon="https://picsum.photos/200",
            # default=(len(profiles) == 0),
        )
        for chain in chains
    ]
    print(profiles)
    return profiles


@cl.on_chat_start
async def on_chat_start():
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    await cl.Message(content=f"{chat_profile}").send()


@cl.on_message
async def on_message(message: cl.Message):
    reply = cl.Message(content="", elements=[])
    chat_profile = cl.user_session.get("chat_profile")

    runnable = next((d["chain"] for d in chains if d["name"] == chat_profile), None)

    if "rag_" in chat_profile:
        # Stream a reply message
        async for chunk in runnable.astream(message.content):
            print(chunk)
            if "answer" in chunk.keys():
                await reply.stream_token(chunk["answer"])
            elif "context" in chunk.keys():
                contexts: List[Document] = chunk["context"]
            elif "question" in chunk.keys():
                question: str = chunk["question"]
        await reply.send()

        # Print intermediates
        print(question)
        for context in contexts:
            if "id" in context.metadata.keys():
                printline = str(context.metadata["id"])
            else:
                printline = "?"
            printline += f"({context.metadata["file_path"]}): "
            if "relevance_score" in context.metadata.keys():
                printline += f"{context.metadata["relevance_score"]}"
            print(printline)

        # Add documents referenced by RAG to a reply
        for context in contexts:
            # Skip added documents
            context_path = os.path.abspath(context.metadata["file_path"])

            # Add fragment to element
            el_flag = False
            for element in reply.elements:
                if context_path == element.name:
                    element.content += "\n- - - - - -\n"
                    element.content += context.page_content
                    el_flag = True
                    continue

            # Add document as element
            if el_flag:
                continue
            reply.elements.append(
                cl.Text(
                    name=context_path,
                    # language=context.metadata["file_type"],
                    content=context.page_content,
                    # path=context_path
                )
            )
    else:
        async for chunk in runnable.astream(
            message.content,
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await reply.stream_token(chunk.content)
        await reply.send()
