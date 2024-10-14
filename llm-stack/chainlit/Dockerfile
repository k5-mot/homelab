FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
# FROM mcr.microsoft.com/devcontainers/base:jammy



# Setup workspace
COPY ./ /home/vscode/chainlit
WORKDIR /home/vscode/chainlit
RUN chown -R vscode:vscode /home/vscode/chainlit
USER vscode

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# RUN pip install --no-cache-dir black flake8 isort
# RUN pip install --no-cache-dir --upgrade \
#     langchain langchain-core langchain-community \
#     langchain-anthropic langchain-openai \
#     langchain-chroma chromadb \
#     langchain-ollama ollama \
#     langchain-elasticsearch \
#     flashrank chainlit

# Run any command to initialize the container
EXPOSE 8000
CMD ["sleep", "infinity"]
# CMD ["chainlit", "run", "app.py"]
