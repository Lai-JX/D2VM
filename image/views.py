from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from django.db.models import Q
from .serializers import ImageSerializer
from .models import Image


class ImageViewSet(viewsets.GenericViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
        
    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Please log in first'})
        
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
    
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'status': status.HTTP_401_UNAUTHORIZED, 'message': 'Please log in first'})
        
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
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)