import json
import re

from rest_framework import serializers

from auth_.models import User
from common import messages
from common.constants import USER_ROLES
from core.models import City


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'avatar']

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)


class UserDetailsSerializer(UserSerializer):
    roles = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['roles', 'username', 'email', 'is_active', 'date_joined']

    def get_roles(self, obj):
        roles = dict(USER_ROLES)
        return roles[obj.roles]


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate_first_name(self, value):
        if not value.isalpha():
            raise Exception(messages.NOT_ALL_LETTERS)
        return value

    def save(self):
        User.objects.create_user(self.validated_data['username'],
                                 self.validated_data['password'],
                                 self.validated_data['email'],
                                 self.validated_data['first_name'],
                                 self.validated_data['last_name'])


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
    new_password_repeat = serializers.CharField(max_length=100)

    def validate(self, attrs):
        if len(attrs['new_password']) < 8:
            raise Exception(messages.PASSWORD_LENGTH_SHORT)
        if attrs['new_password'] != attrs['new_password_repeat']:
            raise Exception(messages.PASSWORDS_NOT_SAME,)
        return attrs

    def change_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class ChangeDetailsSerializer(serializers.Serializer):
    cur_city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    phone = serializers.CharField(max_length=16)

    def validate_phone(self, value):
        if value and not re.search("[+]\d[ ]?[-]?[(]?\d{3}[)]?[ ]?[-]?\d{3}[ ]?[-]?[ ]?\d{2}[ ]?[-]?[ ]?\d{2}", value):
            raise Exception(messages.INCORRECT_PHONE_FORMAT)
        return value

    def validate_cur_city(self, value):
        if not City.objects.filter(id=value).first():
            raise Exception(messages.NO_CITY)
        return value

    def change_details(self):
        user = self.context['request'].user
        if self.validated_data.get('phone'):
            user.profile.phone = self.validated_data['phone']
            user.profile.save()
        json_data = json.loads(json.dumps(self.validated_data))
        for key, value in json_data.items():
            setattr(user, key, value)
        user.save()