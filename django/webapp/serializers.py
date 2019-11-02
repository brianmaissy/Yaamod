
from rest_framework.serializers import ModelSerializer, CharField
from webapp.models import Synagogue
from django.contrib.auth.models import User, Group


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class SynagogueSerializer(ModelSerializer):
    user = UserSerializer(write_only=True)

    class Meta:
        model = Synagogue
        fields = ('name', 'user')

    def create(self, validated_data):
        admins = Group.objects.create(name=u'synagogue_{0}_admins'.format(validated_data['name']))
        validated_data['admins'] = admins
        user_data = validated_data.pop('user')

        synagogue = Synagogue.objects.create(**validated_data)
        user = User.objects.create(**user_data)
        user.groups.add(admins)

        return synagogue
