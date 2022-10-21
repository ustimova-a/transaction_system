from rest_framework import serializers
from django.contrib.auth.models import User 
from .models import Account

class AccountSerializer(serializers.Serializer):
    balance = serializers.FloatField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created = serializers.DateTimeField()

class ExtendedAccountSerializer(serializers.ModelSerializer):

     class Meta:
        model = Account
        fields = ('balance', 'user', 'created')