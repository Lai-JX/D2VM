#! /bin/bash

echo "for item in \$(cat /proc/1/environ |tr '\\0' '\\n');
do
 export \$item;
done" >> /etc/profile;

if ! [ -x "$(command -v ssh)" ] || ! [ -x "$(command -v curl)" ]; 
then
    cp /etc/apt/sources.list /etc/apt/sources.list.bak
    cat >/etc/apt/sources.list <<EOF                   
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-updates main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-backports main restricted universe multiverse
    deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ jammy-security main restricted universe multiverse
EOF
    apt update; 
fi;

if ! [ -x "$(command -v ssh)" ]; 
then
    echo y|apt install openssh-server; 
fi

if ! [ -x "$(command -v curl)" ]; 
then
    echo y|apt install curl; 
fi
echo "cd /workspace"  >> /root/.bashrc;
echo -e "PermitRootLogin yes" >> /etc/ssh/sshd_config;
