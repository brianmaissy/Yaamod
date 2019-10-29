
from rest_framework.serializers import ModelSerializer, CharField
from webapp.models import Synagogue
from django.contrib.auth.models import User


class SynagogueSerializer(ModelSerializer):
    class Meta:
        model = Synagogue
        fields = ('name',)


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
