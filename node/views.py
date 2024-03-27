from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import NodeSerializer
from .models import Node
from rest_framework import generics
# Create your views here.
class NodeView(generics.ListAPIView):
    serializer_class = NodeSerializer
    queryset = Node.objects.all()
    # 采用token验证
    authentication_classes = [TokenAuthentication]
    # 使用 IsAuthenticated 权限类，确保用户已登录
    permission_classes = [IsAuthenticated]
