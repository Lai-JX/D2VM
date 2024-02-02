from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from .models import Container, Node
from .serializers import ContainerCreateSerializer
from .manage_container import config_job, create_job


class ContainerCreateView(generics.CreateAPIView):
    serializer_class = ContainerCreateSerializer

    def post(self, request, *args, **kwargs):
        # 1. 验证是否登录
        try:
            print('user:', request.user)        
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'message': error_message})
        
        config = request.data
        config['file'] = config['name'] + '-' + config['image']
        # print(type(config),config)
        # print(config)
        # 2. 创建job (VM or Task)
        if config['is_VM']:
            config['backoffLimit'] = 1 
            config['cmd'] = 'sleep ' + str(config['duration']) + ';'
            print("create VM")
        else:
            config['backoffLimit'] = 3
            print("create Task")
        # 创建容器(这里暂时先用配置)
        # config_job(config)
        pod_name, svc_name, node_name, port = create_job(config)
        del config['backoffLimit'], config['file']
        config['pod_name'] = pod_name
        config['svc_name'] = svc_name
        config['port'] = port

        node = Node.objects.get(node_name=node_name)
        config['node'] = node.pk
        # 3. 使用传过来的数据实例化一个序列器
        serializer = self.get_serializer(data=config) 
        
        
        # 4. 判断数据是否有效并保存（是否符合序列器要求，会调用validate）
        try:
            serializer.is_valid(raise_exception=True)       
            # validated_data = serializer.validated_data 
            # print(validated_data) 
            serializer.save()                               # 保存
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'status': status.HTTP_403_FORBIDDEN , 'message': error_message})

        return Response({'status': status.HTTP_201_CREATED, 'message': 'success', 'port': port, 'IP': node.node_ip})

# class ContainerViewSet(viewsets.ModelViewSet):
#     queryset = Container.objects.all()      # 对象
#     serializer_class = ContainerSerializer  # 序列化类