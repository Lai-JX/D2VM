from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .serializers import ImageSerializer
from .models import Image
from container.models import Container
from user.models import User
from django.conf import settings
from .manage_image import add_image, commit_image, delete_image, delete_registery_image, push_image, sync_image_to_database

import socket


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

class ImageViewSet(viewsets.GenericViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
    
    # 添加镜像
    def create(self, request, *args, **kwargs):
        image = request.data
        image['source'] = 'public'
        image['is_push'] = True
        print(image)
        serializer = self.get_serializer(data=image)
        if settings.DOCKER_PULL_PUSH_IP == get_host_ip():
            ssh = ''
        else:
            ssh = 'ssh jxlai@' + settings.DOCKER_PULL_PUSH_IP
        res = add_image(ssh, settings.REGISTERY_PATH, image['name']+":"+image['tag'])
        if res == 'image pull fail' or res == 'push fail':
            return Response({'message': res}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save() # TODO
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'message': error_message}, status=status.HTTP_403_FORBIDDEN)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # 获取所有镜像
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'message': 'Please log in first'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # registry_url = settings.REGISTERY_PATH

        # get_all_images_and_tags(registry_url)

        # return

        # 获取用户名
        username = request.user.username
        print(username)
        # queryset = self.filter_queryset(self.get_queryset().filter(source=username))
        queryset = self.filter_queryset(self.get_queryset().filter(Q(source=username) | Q(source='public')))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def delete(self, request, *args, **kwargs):
        image_id = self.request.query_params.get('image_id')
        delete_opt = int(self.request.query_params.get('delete_opt'))
        print(image_id,  delete_opt)

        image = Image.objects.get(image_id=image_id)
        if image.node == None:          # 删除过本地后，image.node就是None
            ssh = 'ssh jxlai@' + settings.DOCKER_PULL_PUSH_IP
        else:
            ssh = 'ssh jxlai@' + image.node.node_ip
        if delete_opt == 2:                 # delete all
            flag1, res1 = delete_registery_image(settings.REGISTERY_PATH, image)
            flag2, res2 = delete_image(ssh, settings.REGISTERY_PATH, image)
            if flag1 and flag2:
                # image.delete()
                return Response({'message':res1+'\n'+res2}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message':res1+'\n'+res2}, status=status.HTTP_403_FORBIDDEN)
        elif delete_opt == 0 and image.node is not None:               # delete local
            print("delete local")
            flag, res = delete_image(ssh, settings.REGISTERY_PATH, image)
            if flag:
                return Response({'message':res}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message':res}, status=status.HTTP_403_FORBIDDEN)
        elif delete_opt == 1:               # delete image in registry
            flag, res = delete_registery_image(settings.REGISTERY_PATH, image)
            if flag:
                return Response({'message':res}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message':res}, status=status.HTTP_403_FORBIDDEN)
        else:
            print("forbidden")
            return Response({'message':'error parameter'}, status=status.HTTP_403_FORBIDDEN)
            


# 用于将容器保存为镜像
class ImageSaveView(generics.GenericAPIView):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 获取容器
        if 'container_id' in self.request.query_params:
            container_id = self.request.query_params.get('container_id')
            container = Container.objects.get(container_id=container_id)
        else: 
            username = self.request.query_params.get('username')
            image = self.request.query_params.get('image').split(":")
            user = User.objects.get(username=username)
            image = Image.objects.get(name=":".join(image[:-1]), tag=image[-1])
            container = Container.objects.get(user=user, image=image)
        # 保存容器
        # ssh到别的机器
        ssh = 'ssh jxlai@' + container.node.node_ip
        flag, res = commit_image(ssh, container, settings.REGISTERY_PATH)
        if flag:
            return Response({'message':res}, status=status.HTTP_200_OK)
        else:
            return Response({'message':res}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# 用于将镜像上传到仓库
class ImagePushView(generics.GenericAPIView):
    # serializer_class = ImageSerializer
    # queryset = Image.objects.all()

    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 获取镜像
        image_id = self.request.query_params.get('image_id')
        image = Image.objects.get(image_id=image_id)
        ssh = 'ssh jxlai@' + image.node.node_ip
        res = push_image(ssh, settings.REGISTERY_PATH, str(image))
        print(res)
        if res != 'push fail':
            image.is_push = True
            image.save()
            return Response({'message':res}, status=status.HTTP_200_OK)
        else:
            return Response({'message':res}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 为镜像添加note
class ImageAddNoteView(generics.GenericAPIView):
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # sync_image_to_database(settings.REGISTERY_PATH)
        image_id = self.request.query_params.get('image_id')
        note = self.request.query_params.get('note')
        try:
            image = Image.objects.get(image_id=image_id) 
            if image.source != request.user.username:
                return Response({'message': "error user"}, status=status.HTTP_403_FORBIDDEN)
            image.note = note   
            image.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            error_message = str(e)
            print(error_message)
            return Response({'message':error_message}, status=status.HTTP_403_FORBIDDEN)
    
# 管理者专用(Deprecated)
class ImageSyncView(generics.GenericAPIView):
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        sync_image_to_database(settings.REGISTERY_PATH)
        print('patch')
