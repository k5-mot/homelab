FROM python:3
WORKDIR /root/workspace
COPY ./* /root/workspace

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get autoremove -y
RUN pip install --upgrade pip
RUN python -m pip install flake8 black isort python-dotenv 'python-lsp-server[all]'
RUN python -m pip install jupyterlab jupyterlab_code_formatter
RUN python -m pip install -r requirements.txt
