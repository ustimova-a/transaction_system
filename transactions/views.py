from email import message
from django.shortcuts import render
from django.db.models import F, Sum, Count
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage
from django.views.generic import ListView
from django.forms.models import model_to_dict

from .models import Account, Transaction
from .forms import TransactionForm, TransactionFilterForm, AccountFilterForm, OutcomeForm
from .filters import TransactionFilter

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
                # transaction_list = []
                # for account in from_accounts:
                #     transaction_list.append(Transaction(from_account=account, to_account=to_account, amount=amount/accounts_count))
                # Transaction.objects.bulk_create(transaction_list)
                transaction = Transaction.objects.create(to_account=to_account, amount=amount)
                transaction.from_accounts.add(*from_accounts)
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


def account(request, account_id):
    account = Account.objects.get(id=account_id)
    outcomes = account.outcomes.annotate(outcome_amount=Count('from_accounts__id')).order_by('-date_time')
    total_outcomes = outcomes.aggregate(Sum('outcome_amount'))['outcome_amount__sum']
    paginated_outcomes = paginate(request, outcomes, 'outcomes_page')
    incomes = account.incomes.order_by('-date_time')
    total_incomes = incomes.aggregate(Sum('amount'))['amount__sum']
    paginated_incomes = paginate(request, incomes, 'incomes_page')
    return render (request, 'account.html', {'account': account, 'outcomes': paginated_outcomes, 'total_outcomes': total_outcomes, 'incomes': paginated_incomes, 'total_incomes': total_incomes})


def cancel_transaction(request):
    message = ''
    if request.method == 'POST':
        id = request.POST.get('id')
        transaction = Transaction.objects.get(id=id)
        if not transaction.is_cancelled:
            transaction.to_account.balance -= transaction.amount
            transaction.to_account.save()
            transaction.from_accounts.update(balance=F('balance') - transaction.amount/transaction.from_accounts.count())
            transaction.is_cancelled = True
            transaction.save()
            message = f'Transaction No.{transaction.id} has been cancelled.'
        else:
            message = 'Already cancelled.'
    return render(request, 'cancel.html', {'message': message }) #redirect


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})
