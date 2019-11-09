import abc

from django.contrib.auth.models import User, Group
from rest_framework.serializers import ModelSerializer, CharField, PrimaryKeyRelatedField, Serializer

from webapp.models import Synagogue


class SynagoguePermissionCheckMixin:
    @abc.abstractmethod
    def get_synagogue(self):
        pass

    def needs_synagogue_check(self):
        return True


class UserSerializer(ModelSerializer, SynagoguePermissionCheckMixin):
    password = CharField(write_only=True)
    synagogue = PrimaryKeyRelatedField(queryset=Synagogue.objects.all(), write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'synagogue')

    def create(self, validated_data):
        synagogue = validated_data.pop('synagogue', None)
        user = User.objects.create_user(**validated_data)
        if synagogue is not None:
            user.groups.add(synagogue.admins)

        return user

    def get_synagogue(self):
        return self.validated_data['synagogue']

    def needs_synagogue_check(self):
        return self.validated_data.get('synagogue') is not None


class SynagogueSerializer(ModelSerializer):
    class Meta:
        model = Synagogue
        fields = ('name',)

    def create(self, validated_data):
        admins = Group.objects.create(name='synagogue_{0}_admins'.format(validated_data['name']))
        member_creator = User.objects.create_user('{0}_member_creator'.format(validated_data['name']))
        validated_data['admins'] = admins
        validated_data['member_creator'] = member_creator

        synagogue = Synagogue.objects.create(**validated_data)
        self.context['request'].user.groups.add(admins)

        return synagogue


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()


class MakeAddMemberTokenSerializer(Serializer, SynagoguePermissionCheckMixin):
    synagogue = PrimaryKeyRelatedField(queryset=Synagogue.objects.all(), write_only=True)

    def get_synagogue(self):
        return self.validated_data['synagogue']
