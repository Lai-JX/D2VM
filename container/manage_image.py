import subprocess
import sys
from os.path import abspath, join, dirname
# sys.path.insert(0, abspath(dirname(__file__)))
# sys.path.insert(0,'/home/jxlai/k8s')

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# from utils import *

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
def manipulate_string(input_string, container):
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
    # if not manipulated_string.startswith(container):
    #     manipulated_string = container + manipulated_string

    manipulated_string = manipulated_string.split(':')
    print(manipulated_string)
    manipulated_string[-1] = add_prefix(manipulated_string[-1], container)
    manipulated_string = ":".join(manipulated_string)
    return manipulated_string

def commit_image(ssh, image_pre, container):
    # 更新image版本
    image = manipulate_string(image_pre, container)
    command_to_run = '{} docker commit $({} docker ps --filter ancestor={} --format "{{{{.Names}}}}" | grep {}) {}'.format(ssh, ssh, image_pre, container, image)
    # print('run:', command_to_run)
    # 调用终端命令
    output = run_command(command_to_run)
    if output is not None:
        print("Command output:")
        print(output)
        return True
    
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
    ssh = 'ssh jxlai@192.168.1.107'
    image_pre = '10.249.46.189:5000/geosx/ubuntu20.04-gcc9:256-139'
    container = 'lyli'
    print(manipulate_string(image_pre, container))
    # commit_image(ssh, image_pre, container)
    # save_image_serve()
    # delete_image('ssh jxlai@192.168.1.107', 'ubuntu-ssh:v1')
