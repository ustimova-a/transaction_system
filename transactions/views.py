from email import message
from django.shortcuts import render
from django.db.models import F, Sum, Count, Prefetch, Q
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage
from django.core.mail import send_mail
import smtplib, ssl
from django.conf import settings
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
import logging

from .models import Account, Transaction
from .forms import TransactionForm, TransactionFilterForm, AccountFilterForm, OutcomeForm
from .filters import TransactionFilter
from rest_framework import generics
from .serializers import ExtendedAccountSerializer

logger = logging.getLogger('src.transactions.views')


def create_transaction(transaction_user, transaction_data):
    form = TransactionForm(transaction_user, transaction_data)

    if not form.is_valid():
        return form, 'Invalid data for transaction.'

    from_accounts = form.cleaned_data.get('from_accounts')
    # print(from_accounts.query)
    to_account = form.cleaned_data.get('to_account')
    amount = form.cleaned_data.get('amount')
    try:
        transaction = Transaction.create_transaction(to_account, from_accounts, amount)
        message = 'Successful transaction.'
        # send_mail('You received money', 
        #             f'Hello {to_account.user.username}! ${amount} have been transferred to your account #{to_account.id}',
        #             settings.DEFUALT_FROM_EMAIL, [to_account.user.email])
        # email_message = f'''\
        # Subject: You received money
        # To: {to_account.user.email}
        # From: {settings.DEFAULT_FROM_EMAIL}

        # Hello {to_account.user.username}! ${amount} have been transferred to your account #{to_account.id}'''
        # email_server = smtplib.SMTP('smtp.jino.ru', 587)
        # # email_server.ehlo()
        # # email_server.starttls(context=ssl.create_default_context())
        # email_server.login('test@arpix.pro', 'b8de3256')
        # email_server.sendmail(settings.DEFAULT_FROM_EMAIL, to_account.user.email, email_message)
        # email_server.quit()
        logger.info(f'Created new transaction {transaction.id}: {to_account.id} -> {from_accounts} = {amount}')
    except ValueError as error:
        form.add_error('from_accounts', error)
        logger.error(error)
        message = ''
        # for account in from_accounts:
        #     account.balance -= amount/accounts_count
        #     account.save()
        
    return form, message


def paginate(request, objects, url_param):
    paginator = Paginator(objects, 5)
    page_num = request.GET.get(url_param, 1)
    try:
        page = paginator.page(page_num)
    except EmptyPage:
        page = paginator.page(1)
    return page   


# def transaction(request):
#     if request.method == 'POST':
#         form, message = create_transaction(request.user, request.POST)
#     else:
#         form = TransactionForm(request.user)
#         message = ''
#     filter = TransactionFilter\
#         (
#             request.GET, 
#             queryset=Transaction.objects
#                 .filter\
#                     (
#                         Q(to_account__user=request.user)
#                         |
#                         Q(from_accounts__user=request.user)
#                     )
#                 .order_by('-date_time'), 
#             request=request
#         )
#     filter_form = filter.form
#     paginated_qs = paginate(request, filter.qs, 'page')
    
#     return render(request, 'transaction.html', 
#         {
#             'add_transaction_form': form, 
#             'message': message, 
#             'filter': paginated_qs, 
#             'filter_form': filter_form
#         })

class TransactionView(View):
    def post(self, request):
        form, message = create_transaction(request.user, request.POST)
        queryset, filter_form = self.__get_data(request)
        return self.__get_template(request, form, queryset, filter_form)

    def get(self, request):
        form = TransactionForm(request.user)
        message = ''
        queryset, filter_form = self.__get_data(request)
        return self.__get_template(request, form, queryset, filter_form)

    def __get_data(self, request):
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
        return paginated_qs, filter_form
    
    def __get_template(self, request, form, paginated_qs, filter_form):
        return render(request, 'transaction.html', 
            {
                'add_transaction_form': form, 
                'message': message, 
                'filter': paginated_qs, 
                'filter_form': filter_form
            }) 


class TransactionListView(ListView):
    # model = Transaction
    queryset = Transaction.objects.all()
    template_name = 'user_transactions.html'
    context_object_name = 'transaction_list'

    def get_queryset(self):
        return Transaction.objects.filter(to_account__user=self.request.user)


# def account(request, account_id):
#     if not request.user.account_set.filter(id=account_id).exists():
#         return render(request, 'cancel.html', {'message': 'Access denied.' })
#     account = Account.objects.prefetch_related(Prefetch('outcomes', Transaction.objects.annotate(outcome_amount=F('amount') / Count('from_accounts')))).get(id=account_id)
#     outcomes = account.outcomes.order_by('-date_time')
#     total_outcomes = outcomes.aggregate(Sum('outcome_amount'))['outcome_amount__sum']
#     paginated_outcomes = paginate(request, outcomes, 'outcomes_page')
#     incomes = account.incomes.order_by('-date_time')
#     total_incomes = incomes.aggregate(Sum('amount'))['amount__sum']
#     paginated_incomes = paginate(request, incomes, 'incomes_page')
#     return render(request, 'account.html', {'account': account, 'outcomes': paginated_outcomes, 'total_outcomes': total_outcomes, 'incomes': paginated_incomes, 'total_incomes': total_incomes})


class AccountView(DetailView):
    model = Account
    template_name = 'account.html'
    context_object_name = 'account'
    pk_url_kwarg = 'account_id'

    def get(self, request, account_id):
        if not request.user.account_set.filter(id=account_id).exists():
            return render(request, 'cancel.html', {'message': 'Access denied.' })
        super().get(request)

    def get_context_data(self):
        context = super().get_context_data()
        account = self.get_object()
        outcomes = account.outcomes.order_by('-date_time')
        context['outcomes'] = outcomes
        context['total_outcomes'] = outcomes.aggregate(Sum('outcome_amount'))['outcome_amount__sum']
        context['paginated_outcomes'] = paginate(self.request, outcomes, 'outcomes_page')
        incomes = account.incomes.order_by('-date_time')
        context['incomes'] = incomes
        context['total_incomes'] = incomes.aggregate(Sum('amount'))['amount__sum']
        context['paginated_incomes'] = paginate(self.request, incomes, 'incomes_page')
        return context


def cancel_transaction(request):
    message = ''
    if request.method == 'POST':
        id = request.POST.get('id')
        # transaction = Transaction.objects.get(id=id)
        transaction = Transaction.objects.get(amount=500)
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


class AccountAPIView(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = ExtendedAccountSerializer

    # def get(self):
    #     account = self.get_object()