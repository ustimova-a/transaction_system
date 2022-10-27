from rest_framework import serializers
from django.contrib.auth.models import User 
from .models import Account, Transaction


class AccountSerializer(serializers.Serializer):
    balance = serializers.FloatField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created = serializers.DateTimeField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class ExtendedAccountSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    user = serializers.StringRelatedField()
    # transactions = TransactionSerializer(many=True, lookup_field='to_account')

    class Meta:
        model = Account
        fields = ('balance', 'user', 'created', 'transactions')