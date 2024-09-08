# FROM quay.io/jupyterhub/jupyterhub:5.1.0
FROM docker.io/ubuntu:jammy
USER root
ENV HOME="/root"
ENV PYENV_ROOT="$HOME/.pyenv"
ENV VOLTA_HOME="$HOME/.volta"
# ENV NVM_DIR="$HOME/.nvm"
ENV PATH="$PYENV_ROOT/bin:$VOLTA_HOME/bin:$PATH"
ENV JUPYTERHUB_SERVICE_URL="http://localhost:8000/"
WORKDIR /root/workspace

RUN apt-get update
RUN apt-get install -y curl wget vim git iputils-ping net-tools

# https://github.com/pyenv/pyenv/wiki#suggested-build-environment
RUN DEBIAN_FRONTEND=noninteractive TZ=TZ=Asia/Tokyo apt-get install -y tzdata
RUN apt-get install -y \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl git libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# https://github.com/nodejs/node/blob/main/BUILDING.md#building-nodejs-on-supported-platforms
RUN apt-get install -y python3 g++ make python3-pip
RUN apt-get install -y --no-install-recommends fonts-noto-cjk
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN apt-get clean
RUN rm -r /var/lib/apt/lists/*

# RUN useradd -s /bin/bash --uid 2525 -m admin
# RUN useradd admin
# RUN echo -e "password\npassword" | passwd admin
# # RUN apt-get install -y sudo
# RUN gpasswd -a admin sudo


RUN curl https://pyenv.run | bash
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
RUN echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN eval "$(pyenv init -)"
RUN pyenv install 3.12.5
RUN pyenv local   3.12.5

RUN pip install --upgrade pip wheel setuptools
RUN pip install --upgrade jupyterhub jupyterlab notebook
RUN pip install ipywidgets jupyter_client dockerspawner
RUN pip install netifaces

# RUN pip install --no-cache-dir numpy pandas scipy opencv-python matplotlib Pillow scikit-learn optuna keras
# RUN pip install --no-cache-dir jupyterhub notebook jupyterlab netifaces
# RUN pip install --no-cache-dir jupyterlab_code_formatter jupyterlab-git lckr-jupyterlab-variableinspector jupyterlab_widgets ipywidgets import-ipynb jupyterlab-language-pack-ja-JP

RUN curl https://get.volta.sh | bash
RUN volta install node@20
RUN npm install -g npm
RUN npm install -g configurable-http-proxy

# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
# RUN echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
# RUN echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
# RUN . $NVM_DIR/nvm.sh \
#     && nvm install 20 \
#     && nvm alias default 20 \
#     && nvm use default \
#     && npm install -g npm \
#     && npm install -g configurable-http-proxy

# ENV NODE_PATH=$NVM_DIR/v20/lib/node_modules
# ENV PATH=$NVM_DIR/versions/node/v20/bin:$PATH

# CMD ["jupyterhub-singleuser", "--allow-root", "-f", "/etc/jupyterhub/jupyterhub_config.py"]
CMD ["jupyterhub", "--no-ssl", "-f", "/etc/jupyterhub/jupyterhub_config.py"]
# CMD ["npm", "list"]
