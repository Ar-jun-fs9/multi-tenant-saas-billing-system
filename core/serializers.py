from rest_framework import serializers
from .models import User, Organization
from .models import Subscription, Plan

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'organization']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash the password
        user.save()
        return user


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
