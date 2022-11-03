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


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password')


class CreateAccountSerializaer(serializers.ModelSerializer):
    user = CreateUserSerializer()

    class Meta:
        model = Account
        fields = ('balance', 'user')


    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(username=user_data['username'], password=user_data['password'])
        # return Account.objects.create(balance=validated_data['balance'], user=user)
        validated_data.update({'user': user})
        return super().create(validated_data)