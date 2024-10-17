import re
from langserve import add_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chains import getLLMChains, getRAGChains

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

chains = []
chains.extend(getLLMChains())
chains.extend(getRAGChains())
for chain in chains:
    print(chain.name)
    name = re.sub(":", "_", chain.name)
    name = re.sub("-", "_", name)
    # name = re.sub(".", "_", name)
    add_routes(
        app=app,
        runnable=chain,
        path=f"/{name}",
    )

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0", port=8000, root_path="/langserve")
    uvicorn.run(app, host="0.0.0.0", port=8000)
