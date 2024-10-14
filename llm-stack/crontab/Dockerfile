FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Update package lists
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup crontab
COPY crontab /var/spool/cron/crontabs/root
RUN chmod 0644 /var/spool/cron/crontabs/root
RUN crontab /var/spool/cron/crontabs/root
RUN touch /var/log/cron.log && chmod 0644 /var/log/cron.log

# Setup workspace
COPY ./ /home/vscode/crontab
WORKDIR /home/vscode/crontab
RUN chown -R vscode:vscode /home/vscode/crontab
USER vscode

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir black flake8 isort
RUN python3 -m pip install --no-cache-dir --upgrade \
    langchain langchain-core langchain-community \
    langchain-text-splitters \
    langchain-anthropic langchain-openai \
    langchain-chroma chromadb \
    langchain-ollama ollama \
    langchain-elasticsearch \
    langchain-unstructured \
    unstructured \
    PyMuPDF spacy python-magic flashrank chainlit
RUN python3 -m spacy download ja_core_news_lg

# Run any command to initialize the container
CMD [ "sudo", "cron", "&&", "sudo", "tail", "-f", "/var/log/cron.log" ]
