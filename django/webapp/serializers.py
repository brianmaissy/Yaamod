from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField, Serializer
from rest_framework.exceptions import ValidationError

from webapp.models import Synagogue, Person, UserToSynagogue
from webapp.utils import request_to_synagogue, request_has_synagogue


def add_user_to_synagogue(user, synagogue):
    UserToSynagogue.objects.create(user=user, synagogue=synagogue)


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        request = self.context['request']
        if request_has_synagogue(request):
            add_user_to_synagogue(user, request_to_synagogue(request))
        return user


class SynagogueSerializer(ModelSerializer):
    class Meta:
        model = Synagogue
        fields = ('name',)

    def create(self, validated_data):
        request = self.context['request']
        if request_has_synagogue(request):
            raise ValidationError('user already has a synagogue')

        member_creator = User.objects.create_user('{0}_member_creator'.format(validated_data['name']))
        validated_data['member_creator'] = member_creator

        synagogue = Synagogue.objects.create(**validated_data)
        add_user_to_synagogue(request.user, synagogue)

        return synagogue


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ('first_name', 'last_name', 'gender_name', 'paternal_name', 'maternal_name', 'yichus_name',
                  'father_json', 'mother_json', 'wife_json', 'num_of_children')

    def create(self, validated_data):
        request = self.context['request']
        validated_data['synagogue'] = request_to_synagogue(request)
        return Person.objects.create(**validated_data)
