from rest_framework.serializers import ModelSerializer

from shop.softwaremodules.models import Softwaremodule


class SoftwaremoduleSerializer(ModelSerializer):
    class Meta:
        model = Softwaremodule
        fields = ('code', 'data',)