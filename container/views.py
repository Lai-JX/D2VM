
import copy
import subprocess
import uuid

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Max, OuterRef, Subquery
from .models import Container
from node.models import Node
from user.models import User
from image.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from .serializers import ContainerSerializer, ContainerGetSerializer
from .manage_container import delete_job, docker_restart, get_pod_status, create_job, get_pod_status_by_username, run_command
from image.manage_image import commit_image


class ContainerView(viewsets.GenericViewSet):
    serializer_class = ContainerSerializer
    queryset = Container.objects.all()
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        
        config = copy.deepcopy(request.data)
        print(config)
        # 1. 根据镜像id获取实际的镜像
        try:
            image = Image.objects.get(image_id=config['image_id'])
            config['image'] = str(image)
            del config['image_id']
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN )
        
        username = config['name']
        config['job_name'] = config['name'] + '-' + str(uuid.uuid1())[:5]
        config['file'] = config['job_name'] + '-' + config['image'].replace('/','-')

        # 2. 创建job (VM or Task)
        if config['is_VM']:
            config['backoffLimit'] = 0 
            config['cmd'] = 'sleep ' + str(config['duration']) + ';'        # 暂时先不考虑cmd字段，启动脚本不会运行cmd，而是根据duration来sleep
            print("create VM")
        else:
            config['backoffLimit'] = 3
            print("create Task")
        # 创建容器
        res = {}    # pod_name, svc_name, node_name, port, path, status
        is_success = create_job(config, res)
        if not is_success:
            return Response({'message': res['err_message']}, status=status.HTTP_403_FORBIDDEN)
        
        config['pod_name'] = res['pod_name']
        config['svc_name'] = res['svc_name']
        config['port'] = res['port']
        config['status'] = res['status']
        config['duration'] = config['duration']/3600    # 转换为小时
        with open(res['path'], 'rb') as file:
            file_content = file.read()
            uploaded_file = SimpleUploadedFile(
                name=config['file']+'.yaml',
                content=file_content,
                content_type='text/plain'
            )
            config['file'] = uploaded_file

        try:
            node = Node.objects.get(node_name=res['node_name'])
            config['node'] = node.pk
            print("update gpu num")
            # 更新剩余gpu数
            node.gpu_remain_num -= config['num_gpu']
            node.save()
        except Node.DoesNotExist:       # 容器为pending
            node = None
        # 3. 判断数据是否有效并保存（是否符合序列器要求，会调用validate）
        try:
            print(res['node_name'])
            user = User.objects.get(username=username)
            
            config['user'] = user.pk
            config['image'] = image.pk
            del config['backoffLimit'], config['name']

            # 使用传过来的数据实例化一个序列器
            # 检查是否存在符合 pod_name 条件的实例
            existing_instance = Container.objects.filter(pod_name=config['pod_name']).first()

            if existing_instance:
                # 存在实例，进行更新操作
                print(res['pod_name'], 'update')
                serializer = self.get_serializer(instance=existing_instance, data=config)
            else:
                # 不存在实例，进行创建操作
                print(res['pod_name'], 'create')
                serializer = self.get_serializer(data=config)

            serializer.is_valid(raise_exception=True)    
            # validated_data = serializer.validated_data 

            serializer.save()                               # 保存
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)

        return Response({'message': 'success', 'port': res['port'], 'IP': None if node is None else node.node_ip}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        # container_id = self.request.query_params.get('container_id')
        # 1. 来自用户delete
        if 'container_id' in self.request.query_params:
            container_id = self.request.query_params.get('container_id')
            try:
                container = Container.objects.get(container_id=container_id)
                if container.user != request.user and not request.user.is_staff:
                    return Response({'message': "error user"}, status=status.HTTP_403_FORBIDDEN)
                print('delete', container.pod_name)
                file_path = settings.POD_CONFIG + container.file.name
                error_message = delete_job(file_path)
                if error_message is not None:
                    return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)
                container_status_pre = container.status
                container.status = get_pod_status(container.pod_name)
                container.save()
                # TODO 判断container是不是pending
                # 更新GPU数
                if container_status_pre != 'Pending':
                    container.node.gpu_remain_num += container.num_gpu
                    container.node.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                # 捕获并处理保存失败的异常
                error_message = str(e)
                print(error_message)
                return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)
        # # 2. 来自job complete前的调用
        # else: 
        #     job_name = self.request.query_params.get('job_name')
        #     image = self.request.query_params.get('image').split(":")
        #     image = Image.objects.get(name=":".join(image[:-1]), tag=image[-1])
        #     container = Container.objects.get(job_name=job_name, image=image)
        #     now = timezone.now()
        #     duration = now - container.create_time
        #     print(duration.total_seconds())
            
        




class ContainerGetView(generics.GenericAPIView):
    
    serializer_class = ContainerGetSerializer       # 只需返回特定的字段
    queryset = Container.objects.all()
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 获取用户名
        username = request.user.username
        print(username)

        # 获取当前用户的pod
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            pod_status, nodes = get_pod_status_by_username(request.user.username, True)       #  # {pod_name:status} {pod_name:node}
        else:
            queryset = self.filter_queryset(self.get_queryset().filter(Q(user=request.user)))
            pod_status, nodes = get_pod_status_by_username(request.user.username)       #  # {pod_name:status} {pod_name:node}
        print(pod_status,nodes)
        # 更新pod状态和所属节点
        for pod in queryset:
            if pod.pod_name in pod_status:
                pod_status_pre = pod.status
                pod.status = pod_status[pod.pod_name]
                try:
                    node = Node.objects.get(node_name=nodes[pod.pod_name])
                    pod.node = node
                    if pod_status_pre == 'Pending':             # 更新GPU数
                        node.gpu_remain_num -= pod.num_gpu
                        node.save()
                except Node.DoesNotExist:       # 容器为pending
                    pod.node = None
                if pod.is_committing:                           # 正属于提交状态
                    pod.status = 'Committing'
            else:
                pod.status = 'Not exist or finished'
            pod.save()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# 重启容器
class ContainerDockerRestartView(generics.GenericAPIView):
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print("docker restart")
        container_id = self.request.query_params.get('container_id')
        try:
            container = Container.objects.get(container_id=container_id) 
            if container.user != request.user and not request.user.is_staff:
                return Response({'message': "error user"}, status=status.HTTP_403_FORBIDDEN)
            if docker_restart(container):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response({'message':error_message}, status=status.HTTP_403_FORBIDDEN)
        
# delete service and conmmit images
class ContainerDeleteServiceView(generics.GenericAPIView):
    # 采用token验证
    # authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print("delete service")
        try:
            job_name = self.request.query_params.get('job_name')
            image = self.request.query_params.get('image').split(":")
            image = Image.objects.get(name=":".join(image[:-1]), tag=image[-1])
            container = Container.objects.get(job_name=job_name, image=image)
            now = timezone.now()
            print(container.job_name,'create_time:', container.create_time, 'current time:', now)
            duration = now - container.create_time
            print('  duration:',duration.total_seconds())
            if duration.total_seconds()+settings.TIME_WAIT_FOR_APPLY+5 > container.duration:
                try:
                    # 删除svc
                    subprocess.run('kubectl delete svc {}'.format(container.svc_name), shell=True, check=True)
                    # 标志处于提交状态
                    container.is_committing = True
                    container.save()
                    # 保存容器
                    ssh = 'ssh jxlai@' + container.node.internal_ip  # ljx_change
                    flag, res = commit_image(ssh, container, settings.REGISTERY_PATH, auto=True)
                    if flag:
                        print("  commit successfully!")
                    else:
                        print("  commit fail!")
                    
                    # 更新GPU数
                    container.node.gpu_remain_num += container.num_gpu
                    container.node.save()
                    # 解除提交状态
                    container.is_committing = False
                    container.save()
                    print('  kubectl delete svc {} successful'.format(container.svc_name))
                except subprocess.CalledProcessError as e:
                    error_message = 'Error executing kubectl delete svc:'+ str(e)
                    print(error_message)
                    return Response({'message':error_message}, status=status.HTTP_403_FORBIDDEN)
                return Response(status=status.HTTP_200_OK)

        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response({'message':error_message}, status=status.HTTP_403_FORBIDDEN)


# class ContainerViewSet(viewsets.ModelViewSet):
#     queryset = Container.objects.all()      # 对象
#     serializer_class = ContainerSerializer  # 序列化类