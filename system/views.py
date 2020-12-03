import logging
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from django_celery_beat.models import PeriodicTask

from .serializers import *
from .models import *

# Create your views here.
logger = logging.getLogger('log')


class LogoutView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


# class TaskViewSet(ModelViewSet):
#     queryset = PeriodicTask.objects.all()
#     serializer_class = TaskSerializer
class PositionViewSet(ModelViewSet):
    perms_map = {'get': '*', 'post': 'position_create', 'put': 'position_update', 'delete': 'position_delete'}
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    pagination_class = None
    search_fields = ['name', 'description']
    ordering_fields = ['pk']
    ordering = ['pk']