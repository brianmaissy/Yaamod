
from rest_framework.serializers import ModelSerializer, CharField, PrimaryKeyRelatedField
from webapp.models import Synagogue
from django.contrib.auth.models import User, Group


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class AddUserSerializer(UserSerializer):
    synagogue = PrimaryKeyRelatedField(queryset=Synagogue.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('synagogue',)

    def create(self, validated_data):
        synagogue = validated_data.pop('synagogue')
        user = User.objects.create(**validated_data)
        user.groups.add(synagogue.admins)
        return user


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
        user = User.objects.create_user(**user_data)
        user.groups.add(admins)

        return synagogue
