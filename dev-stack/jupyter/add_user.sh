#!/bin/bash

USERNAME=""
PASSWORD="password"
# ユーザー追加、パスワード固定
useradd -s /bin/bash -m ${USERNAME} && echo -e "${PASSWORD}\n${PASSWORD}" | passwd ${USERNAME}
# sudoグループに追加
gpasswd -a ${USERNAME} sudo
