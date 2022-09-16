from email import message
from django.shortcuts import render
from django.db.models import F, Sum, Count, Prefetch, Q
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage

from .models import Account, Transaction
from .forms import TransactionForm, TransactionFilterForm, AccountFilterForm, OutcomeForm
from .filters import TransactionFilter


def create_transaction(transaction_user, transaction_data):
    form = TransactionForm(transaction_user, transaction_data)

    if not form.is_valid():
        return form, 'Invalid data for transaction.'

    from_accounts = form.cleaned_data.get('from_accounts')
    # print(from_accounts.query)
    to_account = form.cleaned_data.get('to_account')
    amount = form.cleaned_data.get('amount')
    try:
        Transaction.create_transaction(to_account, from_accounts, amount)
        message = 'Successful transaction.'
    except ValueError as error:
        form.add_error('from_accounts', error)
        message = ''
        # for account in from_accounts:
        #     account.balance -= amount/accounts_count
        #     account.save()
        
    return form, message


def transaction(request):
    if request.method == 'POST':
        form, message = create_transaction(request.user, request.POST)
    else:
        form = TransactionForm(request.user)
        message = ''
    filter = TransactionFilter\
        (
            request.GET, 
            queryset=Transaction.objects
                .filter\
                    (
                        Q(to_account__user=request.user)
                        |
                        Q(from_accounts__user=request.user)
                    )
                .order_by('-date_time'), 
            request=request
        )
    filter_form = filter.form
    paginated_qs = paginate(request, filter.qs, 'page')
    
    return render(request, 'transaction.html', 
        {
            'add_transaction_form': form, 
            'message': message, 
            'filter': paginated_qs, 
            'filter_form': filter_form
        })


def paginate(request, objects, url_param):
    paginator = Paginator(objects, 5)
    page_num = request.GET.get(url_param, 1)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(1)
    return page    


def account(request, account_id):
    if not request.user.account_set.filter(id=account_id).exists():
        return render(request, 'cancel.html', {'message': 'Access denied.' })
    account = Account.objects.prefetch_related(Prefetch('outcomes', Transaction.objects.annotate(outcome_amount=F('amount') / Count('from_accounts')))).get(id=account_id)
    outcomes = account.outcomes.order_by('-date_time')
    total_outcomes = outcomes.aggregate(Sum('outcome_amount'))['outcome_amount__sum']
    paginated_outcomes = paginate(request, outcomes, 'outcomes_page')
    incomes = account.incomes.order_by('-date_time')
    total_incomes = incomes.aggregate(Sum('amount'))['amount__sum']
    paginated_incomes = paginate(request, incomes, 'incomes_page')
    return render(request, 'account.html', {'account': account, 'outcomes': paginated_outcomes, 'total_outcomes': total_outcomes, 'incomes': paginated_incomes, 'total_incomes': total_incomes})


def cancel_transaction(request):
    message = ''
    if request.method == 'POST':
        id = request.POST.get('id')
        transaction = Transaction.objects.get(id=id)
        if transaction.from_accounts.first().user != request.user:
            message = 'Access denied.'
        else:
            if not transaction.is_cancelled:
                transaction.cancel()
                message = f'Transaction No.{transaction.id} has been cancelled.'
            else:
                message = 'Already cancelled.'
    return render(request, 'cancel.html', {'message': message })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})


def test(request):
    account_list = Account.objects.prefetch_related(Prefetch('outcomes', Transaction.objects.annotate(outcome_amount=F('amount') / Count('from_accounts')))).all()
    # transaction_list = Transaction.objects.select_related('to_account')\
    #                                         .prefetch_related(Prefetch('from_accounts', Account.objects.filter(balance__gte=1000)))\
    #                                         .all()
    return render(request, 'test.html', {'account_list': account_list})