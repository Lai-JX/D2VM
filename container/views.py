import copy
import uuid
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.conf import settings
from django.db.models import Q, Max, OuterRef, Subquery
from .models import Container, Node
from user.models import User
from image.models import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from .serializers import ContainerSerializer, ContainerGetSerializer
from .manage_container import delete_job, docker_restart, get_pod_status, create_job, get_pod_status_by_username


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
        config['file'] = config['job_name'] + '-' + config['image']

        # 2. 创建job (VM or Task)
        if config['is_VM']:
            config['backoffLimit'] = 1 
            config['cmd'] = 'sleep ' + str(config['duration']) + ';'
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
        container_id = self.request.query_params.get('container_id')
        try:
            container = Container.objects.get(container_id=container_id)
            print('delete', container.pod_name)
            file_path = settings.POD_CONFIG + container.file.name
            error_message = delete_job(file_path)
            if error_message is not None:
                return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)
            container.status = get_pod_status(container.pod_name)
            container.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)
        




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
        queryset = self.filter_queryset(self.get_queryset().filter(Q(user=request.user)))
        # # 获取具有最新日期的每个 pod_name 下的唯一记录的完整信息
        # latest_pods = queryset.values('pod_name').annotate(published_date=Max('published_date'))
        # latest_pods = queryset.filter(
        #     pod_name__in=[item['pod_name'] for item in latest_pods],
        #     published_date__in=[item['published_date'] for item in latest_pods]
        # )
        pod_status, nodes = get_pod_status_by_username(request.user.username)
        print(pod_status,nodes)
        # 更新pod状态和所属节点
        for pod in queryset:
            if pod.pod_name in pod_status:
                pod.status = pod_status[pod.pod_name]
                try:
                    node = Node.objects.get(node_name=nodes[pod.pod_name])
                    pod.node = node
                except Node.DoesNotExist:       # 容器为pending
                    pod.node = None
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
            if container.user.username != request.user.username:
                return Response({'message': "error user"}, status=status.HTTP_403_FORBIDDEN)
            if docker_restart(container):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response({'message':error_message}, status=status.HTTP_403_FORBIDDEN)


# class ContainerViewSet(viewsets.ModelViewSet):
#     queryset = Container.objects.all()      # 对象
#     serializer_class = ContainerSerializer  # 序列化类