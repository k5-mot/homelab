#!/bin/bash

### User creation script

USERNAME="${1}"
PASSWORD="${USERNAME}"

useradd -s /bin/bash -m ${USERNAME} && echo -e "${PASSWORD}\n${PASSWORD}" | passwd ${USERNAME}
gpasswd -a ${USERNAME} sudo

mkdir -p /home/${USERNAME}/notebook
chmod 007 /home/${USERNAME}/notebook
