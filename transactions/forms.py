from django import forms
from .models import Account, Transaction


class TransactionForm(forms.ModelForm):
    from_accounts = forms.ModelMultipleChoiceField(queryset=Account.objects.all())
    # to_account = forms.ModelChoiceField(queryset=Account.objects.all())
    # amount = forms.FloatField()
    
    class Meta:
        model = Transaction
        fields = ('to_account', 'amount')