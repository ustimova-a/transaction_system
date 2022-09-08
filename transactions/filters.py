from django_filters import FilterSet
import django_filters
from .models import Transaction, Account
from .forms import TransactionFilterForm, AccountFilterForm

class TransactionFilter(FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['from_accounts'].queryset = Account.objects.filter(user=self.request.user)
        self.form.fields['to_account'].queryset = Account.objects.all()
    class Meta:
        model = Transaction
        fields = ('to_account', 'amount', 'from_accounts', 'date_time')
        form = TransactionFilterForm


# class AccountFilter(FilterSet):
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#     #     self.form.fields['id'].queryset = Account.objects.filter(user=self.request.user)
#     class Meta:
#         model = Account
#         fields = ['id']
#         # form = AccountFilterForm


# class CancelFilter(FilterSet):
    

#     class Meta:
#         model = Transaction
#         fields = 