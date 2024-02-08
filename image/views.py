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
from .manage_image import commit_image, push_image, sync_image_to_database


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
    
    # 提交已有镜像
    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save() # TODO
        except Exception as e:
            # 捕获并处理保存失败的异常
            error_message = str(e)
            print(error_message)
            return Response({'status': status.HTTP_403_FORBIDDEN , 'message': error_message})
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    # 获取所有镜像
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Please log in first'})
        
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
    
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

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
        res = commit_image(container, settings.REGISTERY_PATH)
        return Response({'msg':res})
    
# 用于将镜像上传到仓库
class ImagePushView(generics.GenericAPIView):
    # serializer_class = ImageSerializer
    # queryset = Image.objects.all()

    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 获取容器
        container_id = self.request.query_params.get('container_id')
        push_image()
        
        
    
# 管理者专用(Deprecated)
class ImageSyncView(generics.GenericAPIView):
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        sync_image_to_database(settings.REGISTERY_PATH)
        print('patch')
