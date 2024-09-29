#!/bin/bash

USERNAME="${1}"
PASSWORD="${USERNAME}"

# ユーザー追加、パスワード固定
useradd -s /bin/bash -m ${USERNAME} && echo -e "${PASSWORD}\n${PASSWORD}" | passwd ${USERNAME}
# sudoグループに追加
gpasswd -a ${USERNAME} sudo

mkdir -p /home/${USERNAME}/notebook
chmod 007 /home/${USERNAME}/notebook
