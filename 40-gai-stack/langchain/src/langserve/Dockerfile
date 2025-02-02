FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm
ENV PATH=/home/vscode/.local/bin:$PATH

# Setup workspace
COPY ./ /home/vscode/langserve
WORKDIR /home/vscode/langserve
RUN chown -R vscode:vscode /home/vscode/langserve
USER vscode

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Run any command to initialize the container
EXPOSE 8000
CMD ["python", "server.py"]
