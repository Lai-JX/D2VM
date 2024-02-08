import subprocess
import sys
from os.path import abspath, join, dirname
# sys.path.insert(0, abspath(dirname(__file__)))
# sys.path.insert(0,'/home/jxlai/k8s')

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from django.conf import settings
# from .models import Image

# from utils import *
import requests

# 从私有镜像库获取所有镜像
def get_all_images_and_tags(registry_url):
    registry_url = 'http://' + registry_url
    catalog_url = f"{registry_url}/v2/_catalog"
    response = requests.get(catalog_url)

    image_tags_dict = {}
    if response.status_code == 200:
        catalog_data = response.json()
        image_list = catalog_data.get('repositories', [])

        for image in image_list:
            tags_url = f"{registry_url}/v2/{image}/tags/list"
            tags_response = requests.get(tags_url)

            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                tags = tags_data.get('tags', [])
                if tags is not None:
                    image_tags_dict[image] = tags
                    # print(f"Image: {image}, Tags: {', '.join(tags)}")
            else:
                print(f"Failed to get tags for image {image}. Status Code: {tags_response.status_code}")

    else:
        print(f"Failed to get catalog. Status Code: {response.status_code}")
    return image_tags_dict

def sync_image_to_database(registry_url):
    images = get_all_images_and_tags(registry_url)
    for image, tags in images.items():
        for tag in tags:
            # print(image, tag, Image.objects.filter(name=image, tag=tag).exists())
            print(image, tag)

# 删除镜像库镜像
def delete_registery_image(registry_url, image_name, tag):
    registry_url = 'http://' + registry_url
    manifest_url = f"{registry_url}/v2/{image_name}/manifests/{tag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    
    # 获取哈希值
    response = requests.get(manifest_url, headers=headers)
    
    if response.status_code == 200:
        digest = response.headers.get('Docker-Content-Digest')
        
        # 构造删除请求
        delete_url = f"{registry_url}/v2/{image_name}/manifests/{digest}"
        print(delete_url)
        delete_response = requests.delete(delete_url)

        if delete_response.status_code == 202:
            print(f"Image {image_name}:{tag} deleted successfully.")
        else:
            print(f"Failed to delete image {image_name}:{tag}. Status Code: {delete_response.status_code}")
    else:
        print(f"Failed to get manifest for {image_name}:{tag}. Status Code: {response.status_code}")


def get_image_created_time(registry_url, image_name, tag):
    registry_url = 'http://' + registry_url
    manifest_url = f"{registry_url}/v2/{image_name}/manifests/{tag}"
    headers = {"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
    print(manifest_url)
    response = requests.get(manifest_url, headers=headers)

    if response.status_code == 200:
        manifest_data = response.json()
        print(response.headers)
        print(manifest_data)
        created_time = manifest_data.get('history')[0].get('v1Compatibility', {}).get('created')
        return created_time
    else:
        print(f"Failed to get manifest for {image_name}:{tag}. Status Code: {response.status_code}")
        return None

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

def add_prefix(text, prefix):
    prefix = prefix + '-'
    if not text.startswith(prefix):
        text = prefix + text
    return text

# 更新镜像版本号
def manipulate_string(input_string, username):
    # 如果字符串为空，则直接返回 '-1'
    if not input_string:
        return '-1'

    # 获取字符串最后一个字符
    last_character = input_string[-1]

    # 判断最后一个字符是否为数字
    if last_character.isdigit():
        # 如果是数字，则将最后一个字符转换为整数后加 1
        new_last_character = str(int(last_character) + 1)
        # 替换字符串中的最后一个字符为加 1 后的数字
        manipulated_string = input_string[:-1] + new_last_character
    else:
        # 如果不是数字，则在字符串末尾拼接 '-1'
        manipulated_string = input_string + '-1'
    # if not manipulated_string.startswith(username):
    #     manipulated_string = username + manipulated_string

    manipulated_string = manipulated_string.split(':')
    print(manipulated_string)
    manipulated_string[-1] = add_prefix(manipulated_string[-1], username)
    manipulated_string = ":".join(manipulated_string)
    return manipulated_string

def commit_image(ssh, container, register_path):
    # 1. 更新image版本
    image_pre = register_path + '/' + str(container.image)
    
    username = container.user.username
    image = manipulate_string(image_pre, username)
    # 2. 判断镜像名是否已经存在
    command_to_run = ssh + ' docker images -q ' + image
    print('run:', command_to_run)
    # 调用终端命令
    output = run_command(command_to_run)
    if output!='':
        return 'image already exist!'
    
    # 3. 提交镜像
    command_to_run = '{} docker commit $({} docker ps --filter ancestor={} --format "{{{{.Names}}}}" | grep {}) {}'.format(ssh, ssh, image_pre, username, image)
    print('run:', command_to_run)
    output = run_command(command_to_run)
    if output is not None:
        print("Command output:")
        print(output)
        container.commit_image_name = image[len(register_path)+1:]
        container.save()
    return output

def push_image(ssh, register_path, image_name):
    pass

    
def delete_image(ssh, image):
    # TODO:确认镜像是否存在

    # 1. 查看镜像是否被占用
    command_to_run = '{} docker ps --filter ancestor={} --format "{{{{.Names}}}}"'.format(ssh, image)
    output = run_command(command_to_run)
    if output == None:
        return False
    
    if len(output) > 0:
        print("The image is in use!")
        print(output)
        return False
    # 2. 删除镜像
    else:
        command_to_run = '{} docker rmi {}>'.format(ssh, image)
        output = run_command(command_to_run)
        return True

    


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):               # 保存镜像
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        # print(query_params)

        # 获取参数
        if 'container' in query_params and 'image' in query_params:
            container = query_params['container'][0]
            image_pre = query_params['image'][0]

            # TODO
            # 查询此容器在哪个node上运行，这里先写死
            ssh = 'ssh jxlai@192.168.1.107'
            
            output = commit_image(ssh, image_pre, container)
            
            if output:
                self.send_response(200)
                # self.send_header('Content-type', 'text/html')
                self.end_headers()
        else:
            print('parameters errors')
            self.wfile.write(b"not enough parameters")
        

def save_image_serve(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    # ssh = 'ssh jxlai@192.168.1.107'
    # image_pre = '10.249.46.189:5000/ubuntu-ssh:v1'
    # container = 'dsun'
    # print(manipulate_string(image_pre, container))
    # commit_image(ssh, image_pre, container)
    # save_image_serve()
    # delete_image('ssh jxlai@192.168.1.107', 'ubuntu-ssh:v1')

    registry_url = '10.249.46.189:5000'
    # registry_url = 'http://10.249.46.189:5000'
    images = get_all_images_and_tags(registry_url)
    for image, tags in images.items():
        for tag in tags:
            print(image, tag)
            # get_image_created_time(registry_url, image, tag)
    # delete_registery_image(registry_url, 'ubuntu-ssh', 'shou-v4')
    # print(images)
