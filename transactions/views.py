from email import message
from django.shortcuts import render
from django.db.models import F, Sum
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage
from django.views.generic import ListView

from .models import Account, Transaction
from .forms import TransactionForm, TransactionFilterForm, AccountFilterForm, CancelForm
from .filters import TransactionFilter, AccountFilter

def transaction(request):
    message = ''
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            from_accounts = form.cleaned_data.get('from_accounts')
            # print(from_accounts.query)
            to_account = form.cleaned_data.get('to_account')
            amount = form.cleaned_data.get('amount')
            accounts_count = from_accounts.count()
            # for account in from_accounts:
            #     if account.balance < amount/accounts_count:
            #         form.add_error('from_accounts', f'Account {account.id} does not have sufficient funds.')
            #         break
            # print(from_accounts.filter(balance__gte=amount/accounts_count).query)
            if from_accounts.filter(balance__gte=amount/accounts_count).count() < accounts_count:
                form.add_error('from_accounts', f'Account {Account.id} does not have sufficient funds.')
            else:
                # for account in from_accounts:
                #     account.balance -= amount/accounts_count
                #     account.save()
                from_accounts.update(balance=F('balance') - amount/accounts_count)
                to_account.balance += amount
                to_account.save()
                # for account in from_accounts:
                #     Transaction.objects.create(from_account=account, to_account=to_account, amount=amount/accounts_count)
                transaction_list = []
                for account in from_accounts:
                    transaction_list.append(Transaction(from_account=account, to_account=to_account, amount=amount/accounts_count))
                Transaction.objects.bulk_create(transaction_list)
                message = 'Successful transaction.'
    else:
        form = TransactionForm(request.user)
    return render(request, 'transaction.html', {'filter_form': form, 'message': message})


def paginate(request, objects, url_param):
    paginator = Paginator(objects, 5)
    page_num = request.GET.get(url_param, 1)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(1)
    return page    


def filter_transactions(request):
    filter = TransactionFilter(request.GET, queryset=Transaction.objects.all(), request=request)
    filter_form = filter.form
    paginated_qs = paginate(request, filter.qs, 'page')
    return render(request, 'filter_transactions.html', {'filter': paginated_qs, 'filter_form': filter_form})


def cancel_transaction(request, account):
    # message = ''
    if request.method == 'POST':
        form = CancelForm(request.POST)
        if form.is_valid():
            # to_account = Transaction.to_account
            amount = 1
            is_cancelled = form.cleaned_data.get('is_cancelled')
            # to_account.balance -= amount
            # to_account.save()
            account.balance += amount
            account.save()
            # message = 'Cancelled'
    else:
        form = CancelForm()
        return render(request, 'cancel.html', {'form': form})   #'message': message 


def account(request, account_id):
    account = Account.objects.get(id=account_id)
    form = CancelForm(request.POST)
    outcomes = account.outcomes.order_by('-date_time')
    for transaction in outcomes:
        if transaction.is_cancelled == True:
            cancel_transaction(request, transaction)
    total_outcomes = outcomes.aggregate(Sum('amount'))['amount__sum']
    paginated_outcomes = paginate(request, outcomes, 'outcomes_page')
    incomes = account.incomes.order_by('-date_time')
    total_incomes = incomes.aggregate(Sum('amount'))['amount__sum']
    paginated_incomes = paginate(request, incomes, 'incomes_page')
    cancel_transaction(request, account) #???
    return render (request, 'account.html', {'account': account, 'outcomes': paginated_outcomes, 'total_outcomes': total_outcomes, 'incomes': paginated_incomes, 'total_incomes': total_incomes, 'form': form})
    

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})
