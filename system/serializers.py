from rest_framework.serializers import ModelSerializer
from .models import *


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'
