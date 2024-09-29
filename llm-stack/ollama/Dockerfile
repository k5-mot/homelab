FROM docker.io/ollama/ollama:latest
ENV OLLAMA_HOST=0.0.0.0
WORKDIR /workspace
COPY ./ /workspace/

RUN apt-get update && apt-get install -y curl

RUN chmod 755 /workspace/1-setup.sh
RUN chmod 755 /workspace/2-setup.sh
RUN bash /workspace/1-setup.sh
RUN bash /workspace/2-setup.sh

EXPOSE 11434
ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]
