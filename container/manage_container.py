
import subprocess
import yaml
import munch
import copy
import os
import time
from datetime import datetime
from django.conf import settings
import uuid

# 执行终端命令
def run_command(command):
    try:
        # 执行命令并等待返回结果
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 如果命令执行失败，捕获异常并处理
        print(f"Command execution failed with error: {e}")
        return None

def config_job(config):
    with open('pod_config/template/template_job.yaml', 'r', encoding='utf-8') as f:
        template_yaml = yaml.load_all(f.read(), Loader=yaml.FullLoader)
    template_yaml = list(template_yaml)             # 包括pod和service

    job = munch.Munch.fromDict(template_yaml[0])  # 转化为类
    job.metadata.name = 'job-' + config['job_name']
    job.spec.selector.matchLabels.user = config['job_name']
    # 设置重新尝试的次数
    job.spec.backoffLimit = config['backoffLimit']
    
    container = job.spec.template
    service = munch.Munch.fromDict(template_yaml[1])

    # 设置pod的name和label
    container.metadata.name = config['job_name']
    container.metadata.labels.user = config['job_name']

    # 设置gpu类型
    if 'gputype' in config:
        container.spec.nodeSelector.gputype = config['gputype']
    else:
        del container.spec.nodeSelector.gputype

    # 设置主机名
    if 'hostname' in config:
        container.spec.nodeSelector['kubernetes.io/hostname'] = config['hostname']
    else:
        del container.spec.nodeSelector['kubernetes.io/hostname']

    

    # 设置存储卷
    container.spec.volumes[0].name = config['job_name'] + '-volumes'
    container.spec.volumes[0].hostPath.path = '/VM/' + config['name']
    # container.spec.volumes[0].nfs.path = settings.NFS_DIR_PREFIX + config['name']
    # container.spec.volumes[0].nfs.server = settings.NFS_IP
    # container.spec.volumes[1].nfs.path = settings.NFS_DIR_PREFIX + 'share/'
    # container.spec.volumes[1].nfs.server = settings.NFS_IP_SHARE
    if 'shm' in config:
        container.spec.volumes[2].emptyDir.sizeLimit = config['shm']
    else:
        del container.spec.volumes[2]
    # # 在主机上创建存储卷（默认是在同主机,需要确保当前用户可以编辑该目录）
    print(os.system('id'))
    os.system('mkdir {}'.format(container.spec.volumes[0].hostPath.path))
    # os.system('{} mkdir {}'.format(settings.NFS_SSH, container.spec.volumes[0].nfs.path))

    # 设置镜像
    container.spec.containers[0].image = settings.REGISTERY_PATH + '/' + config['image']
    container.spec.containers[0].name = config['job_name']  # 容器名

    # 钩子函数
    container.spec.containers[0].lifecycle.preStop.httpGet.path = f'image/save/?job_name={config["job_name"]}&image={config["image"]}&from=2'    # 传递参数，便于钩子函数保存镜像(Deprecated)
    container.spec.containers[0].lifecycle.preStop.httpGet.host = settings.D2VM_IP
    container.spec.containers[0].lifecycle.preStop.httpGet.port = settings.D2VM_PORT


    # 设置密码和启动命令，以及退出前保存镜像
    tmp = f'curl "http://{settings.D2VM_IP}:{settings.D2VM_PORT}' + f'/container/deleteService/?job_name={config["job_name"]}&image={config["image"]}&from=1";'                        # 通知保存镜像（使用rpc比较好）
    # tmp = ''

    # container.spec.containers[0].args = [ base_cmd + ' echo -e "{}\\n{}\\n"|passwd;  service ssh restart; {} while true; do sleep 3600; done; {}'.format(config['password'], config['password'], config['cmd'], tmp) ]
    # container.spec.containers[0].args = [ base_cmd + ' echo -e "{}\\n{}\\n"|passwd;  service ssh restart; {} {}'.format(config['password'], config['password'], config['cmd'], tmp) ]
    container.spec.containers[0].args = [ '/share/base_cmd.sh; echo -e "{}\\n{}\\n"|passwd;  service ssh restart; {} service ssh stop; service ssh disable; {}'.format(config['password'], config['password'], config['cmd'], tmp) ]

    # 挂载
    container.spec.containers[0].volumeMounts[0].mountPath = config['path']
    container.spec.containers[0].volumeMounts[0].name = container.spec.volumes[0]['name'] 
    if 'shm' not in config:
        del container.spec.containers[0].volumeMounts[2]

    # 资源
    container.spec.containers[0].resources.requests['nvidia.com/gpu'] = config['num_gpu']
    if 'gpumem' in config:
        container.spec.containers[0].resources.requests['nvidia.com/gpumem'] = config['gpumem']
    else:
        del container.spec.containers[0].resources.requests['nvidia.com/gpumem']

    if 'gpucores' in config: 
        container.spec.containers[0].resources.requests['nvidia.com/gpucores'] = config['gpucores']
    else:
        del container.spec.containers[0].resources.requests['nvidia.com/gpucores']
    # 设置临时存储大小限制
    if 'ephemeral_storage' in config:
        container.spec.containers[0].resources.requests['ephemeral-storage'] = config['ephemeral_storage']
    else:
        del container.spec.containers[0].resources.requests['ephemeral-storage']

    container.spec.containers[0].resources.requests['cpu'] = config['cpu']
    container.spec.containers[0].resources.requests['memory'] = config['memory']
    container.spec.containers[0].resources.limits = copy.deepcopy(container.spec.containers[0].resources.requests)

    # 特权
    if 'capabilities' in config: 
        container.spec.containers[0].securityContext.capabilities.add = config['capabilities']

    # 是否在master上运行
    if config['use_master']:
        container.spec.tolerations.append({'key':'node-role.kubernetes.io/master', 'operator': 'Exists', 'effect':'NoSchedule'})

    # 设置service
    service.metadata.name = 'job-ssh-' + config['job_name']
    service.spec.selector.user = config['job_name']
    service.spec.ports[0].nodePort=config['port'] if 'port' in config else None

    # 保存yaml文件
    # 获取当前日期和时间
    current_date = datetime.now().strftime("%Y/%m/%d")
    save_dir = settings.POD_CONFIG + current_date
    os.system('mkdir -p {}'.format(save_dir))
    save_path = '{}/{}.yaml'.format(save_dir, config['file'])
    with open(save_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump_all(documents=[job, service], stream=f, allow_unicode=True)
    return save_path, container.metadata.name, service.metadata.name

def start_job(path, container_name, res):
    try:
        subprocess.run('kubectl apply -f {}'.format(path), shell=True, check=True)
        print('kubectl apply successful')
    except subprocess.CalledProcessError as e:
        error_message = 'Error executing kubectl apply:'+ str(e)
        print(error_message)
        res['err_message'] = error_message
        return False
    
    print(path, container_name)
    time.sleep(settings.TIME_WAIT_FOR_APPLY)
    # 获取pod_name
    # pod_res = os.popen("kubectl get pod -owide | grep {}".format('job-'+container_name+'-'))
    # pod_res = pod_res.read().split('\n')
    # print(pod_res)
    
    # while len(pod_res) == 1:
    #     time.sleep(1)
    #     pod_res = os.popen("kubectl get pod -owide | grep {}".format('job-'+container_name+'-'))
    #     pod_res = pod_res.read().split('\n')
    # if len(pod_res)==1:
    #     # TODO 一般是资源不够或者是无法调度
    #     pass
    pod_name = None
    while pod_name is None:
        pod_res = os.popen("kubectl get pod -owide | grep {}".format('job-'+container_name+'-'))
        pod_res = pod_res.read().split('\n')
        for row in pod_res:
            row = row.split()
            print(row)
            if len(row) > 0 and row[2] != 'Terminating' and row[2] != 'Completed':
                # print(row, row[2])
                pod_name = row[0]
                node_name = row[6]
                status = row[2]
        time.sleep(1)

    # 获取svc_name
    svc_res = os.popen("kubectl get svc | grep {}".format("job-ssh-"+container_name))
    svc_res = svc_res.read().split()
    # print(svc_res[5].split('/')[0].split(':')[1])
    if len(svc_res) > 0:
        svc_name = svc_res[0]
        port = svc_res[4].split('/')[0].split(':')[1]

    res['pod_name'], res['svc_name'], res['node_name'], res['port'], res['path'], res['status'] = pod_name, svc_name, node_name, port, path, status
    return True


def create_job(config, res):

    # 根据要求创建容器（VM or task）
    path, pod_name, svc_name = config_job(config)

    # 启动容器
    return start_job(path, pod_name, res,)    # 返回pod_name, svc_name, port

    # 开启端口(用nodeport也可以)
    # os.system('nohup kubectl port-forward --address 0.0.0.0 svc/{} {}:22 >> ./log/{} 2>&1 &'.format(svc_name,port,pod_name))    # 获取这条命令的进程（ljx-ssh记得替换）：ps -ef | grep forward | grep svc | grep ljx-ssh
    # nohup kubectl port-forward --address 0.0.0.0 svc/kube-prometheus-stack-1701401149-grafana  -n prometheus 32323:80 >> ./k8s/Docker_VM/log/grafana.txt  2>&1 &

def get_pod_status(pod_name):
    res = os.popen("kubectl get pod | grep {}".format(pod_name))
    res = res.read().split('\n')
    # print(res)
    if len(res)==1:
        # pod 不存在
        status = 'Not exist or finished'
    else:
        status = res[0].split()[2]
    print(status)
    return status

def get_pod_status_by_username(username, is_staff=False):
    if is_staff:
        res = os.popen("kubectl get pod -owide | grep -v dcgm-exporter")
    else:
        res = os.popen("kubectl get pod -owide | grep {}".format('job-'+username+'-'))
    res = res.read().split('\n')
    pod_status = {}
    nodes = {}
    for row in res[:-1]:
        row = row.split()
        pod_status[row[0]] = row[2]
        nodes[row[0]] = row[6]
    # # print(res)
    # if len(res)==1:
    #     # pod 不存在
    #     status = 'Not exist or finished'
    # else:
    #     status = res[0].split()[2]
    # print(pod_status)
    return pod_status, nodes        # {pod_name:status} {pod_name:node}
def delete_job(config_file_path):
    try:
        subprocess.run('kubectl delete -f {}'.format(config_file_path), shell=True, check=True)
        print('kubectl delete successful')
        return None
    except subprocess.CalledProcessError as e:
        error_message = 'Error executing kubectl delete:'+ str(e)
        print(error_message)
        return error_message
    
def docker_restart(container):
    ssh = 'ssh jxlai@' + container.node.internal_ip         # ljx_change
    print(container.svc_name)
    command_to_run = '{} docker restart $({} docker ps --format "{{{{.Names}}}}" | grep {})'.format(ssh, ssh, 'k8s_'+ container.job_name)
    print('run:', command_to_run)
    output = run_command(command_to_run)
    if output is not None:
        print("Command output:")
        print(output)
        return True
    else:
        return False

    
if __name__ == '__main__':
    # file_path = 'template/cmd.txt'
    # with open(file_path, 'r') as file:
    #     file_content = file.read().replace('\n', ' ') 

    # print(file_content.replace('\n', ' '))  # 打印文件内容（作为字符串）

    # start_job('1', 'myubuntu')
    get_pod_status_by_username('ljx')