FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
ENV PATH=/home/vscode/.local/bin:$PATH

# Setup workspace
COPY ./ /home/vscode/chainlit
WORKDIR /home/vscode/chainlit
RUN chown -R vscode:vscode /home/vscode/chainlit
USER vscode

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install chainlit langchain langchain-core "langserve[client]"
# python3 -m pip install --no-cache-dir -r requirements.txt

# Run any command to initialize the container
EXPOSE 8000
CMD ["chainlit", "run", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/chainlit", "app.py"]
