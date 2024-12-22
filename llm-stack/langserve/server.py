import re
from typing import List
from langchain_core.runnables import Runnable
from langchain.globals import set_debug, set_verbose
from langserve import add_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chains import get_simple_llm_chains, get_rag_chains


set_debug(False)
set_verbose(False)


app = FastAPI(
    title="LangServe",
    version="1.0",
    description="LangChain API Server",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

chains = [*get_simple_llm_chains(), *get_rag_chains()]

for chain_with_metadata in chains:
    chain = chain_with_metadata["chain"]
    metadata = chain_with_metadata["metadata"]
    print(metadata["path"])
    add_routes(
        app=app,
        runnable=chain,
        path=f"/{metadata["path"]}",
    )


@app.get("/list")
async def list():
    return {"chains": [chain["metadata"] for chain in chains]}


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8000, root_path="/langserve")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
