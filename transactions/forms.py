from django import forms
from .models import Account, Transaction


class TransactionForm(forms.ModelForm):
    from_accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.none())
    # to_account = forms.ModelChoiceField(queryset=Account.objects.all())
    # amount = forms.FloatField()
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_accounts'].queryset = Account.objects.filter(user=user)
    
    class Meta:
        model = Transaction
        fields = ('to_account', 'amount')


class TransactionFilterForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ('to_account', 'amount', 'from_account')


class AccountFilterForm(forms.ModelForm):
    # id = forms.ModelMultipleChoiceField(queryset=Account.objects.none())
    # def __init__(self, user, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['id'].queryset = Account.objects.filter(user=user)

    class Meta:
        model = Account
        fields = ('user', 'id')


class CancelForm(forms.ModelForm):
    is_cancelled = forms.BooleanField(required=False)

    class Meta:
        model = Transaction
        fields = ('is_cancelled',)