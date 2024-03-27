#! /bin/bash
echo -e "\ninit container\n"
echo "for item in \$(cat /proc/1/environ |tr '\\0' '\\n');
do
 export \$item;
done" >> /etc/profile;

chmod 777 /tmp

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

# 设置ssh，并重启服务
# echo "cd /workspace"  >> /root/.bashrc;
if ! grep -q "cd /workspace" "/root/.bashrc"; then
    echo "cd /workspace" >> "/root/.bashrc"
fi

sed -i 's/#PermitRootLogin yes/PermitRootLogin yes/' "/etc/ssh/sshd_config"
# echo -e "PermitRootLogin yes" >> /etc/ssh/sshd_config;
if ! grep -q "PermitRootLogin yes" "/etc/ssh/sshd_config"; then
    echo "PermitRootLogin yes" >> "/etc/ssh/sshd_config"
fi

echo -e "$1\\n$1\\n"|passwd;
service ssh restart; 
/etc/init.d/ssh restart;
echo $1
echo $2
# 指定运行时间
hours=$(( $2 / 3600 ))      # 3600
for i in $(seq $hours); do
    sleep 3600              # 3600
    echo "exec $i hours"
done

service ssh stop; 
service ssh disable; 

