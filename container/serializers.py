from rest_framework import serializers
from .models import Container
from user.models import User

from datetime import datetime

# class ContainerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Container
#         fields = ['name', 'image', 'published_date']

class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = '__all__'

class ContainerGetSerializer(serializers.ModelSerializer):

    image_name = serializers.SerializerMethodField()
    node_ip = serializers.SerializerMethodField()

    class Meta:
        model = Container
        fields = ['container_id', 'pod_name', 'image_name', 'node_ip', 'port', 'gputype', 'num_gpu', 'duration', 'status', 'create_time']
    
    def get_image_name(self, obj):
        return obj.image.name + ':' + obj.image.tag if obj.image else None
    def get_node_ip(self, obj):
        return obj.node.node_ip  if obj.node.node_ip else None
