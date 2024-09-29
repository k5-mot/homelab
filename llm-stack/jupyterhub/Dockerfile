FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-devel

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup packages
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y git tar curl vim sudo \
    && apt-get install -y --no-install-recommends fonts-noto-cjk \
    && apt-get autoremove -y \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Setup Node.js
ENV NVM_VERSION v0.40.1
ENV NVM_DIR /usr/local/nvm
ENV NODE_VERSION v20.17.0
RUN mkdir /usr/local/nvm \
    && curl https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default \
    && npm i -g yarn configurable-http-proxy

# Non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV PATH=/home/${USERNAME}/.local/bin:${PATH}

# Add non-root user
RUN groupadd --gid $USER_GID $USERNAME
RUN useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME
RUN echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME
RUN chmod 0440 /etc/sudoers.d/$USERNAME
RUN echo -e "${USERNAME}\n${USERNAME}" | passwd ${USERNAME}
RUN gpasswd -a ${USERNAME} sudo
RUN mkdir -p /home/${USERNAME}/notebook
RUN chmod 007 /home/${USERNAME}/notebook

# Set the working directory in the container
RUN echo 'export NVM_DIR="/usr/local/nvm"' >> /home/${USERNAME}/.bashrc
RUN echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm' >> /home/${USERNAME}/.bashrc
RUN echo '[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion' >> /home/${USERNAME}/.bashrc

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade jupyterhub notebook jupyterlab oauthenticator \
    && pip install --no-cache-dir netifaces \
    && pip install --no-cache-dir jupyterlab-git
RUN pip install --no-cache-dir \
    jupyterlab_code_formatter black isort  \
    jupyterlab-lsp 'python-lsp-server[all]'

# Setup Jupyterhub
COPY ./add_user.sh /etc/jupyterhub/add_user.sh
RUN chmod 775 /etc/jupyterhub/add_user.sh
WORKDIR /workspace
COPY ./add_config.py /workspace/
RUN jupyterhub --generate-config
RUN cat /workspace/add_config.py >> /workspace/jupyterhub_config.py

ENV PATH="/usr/local/nvm/versions/node/$NODE_VERSION/bin/:$PATH"

EXPOSE 8000
# ENTRYPOINT ["sleep"]
# CMD ["infinity"]
ENTRYPOINT [ "jupyterhub", "--config=/workspace/jupyterhub_config.py" ]
# jupyterhub --config=/home/vscode/notebook/jupyterhub_config.py
