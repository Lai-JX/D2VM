from rest_framework import serializers
from .models import Node



class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        # fields = '__all__'
        fields = ['node_id', 'node_name', 'node_ip', 'gputype', 'gpu_num', 'gpu_remain_num']
    