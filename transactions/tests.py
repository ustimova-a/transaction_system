from django.test import TestCase, Client

from transactions.views import create_transaction
from .models import Account, Transaction
from django.contrib.auth.models import User
import pytest
from django.conf import settings
from unittest.mock import patch

class TransactionTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user1 = User.objects.create_user(username='user1', password='12345', email='stalker-prog@mail.ru')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.user3 = User.objects.create_user(username='user3', password='12345')
        self.account1 = Account.objects.create(balance=1000, user=self.user1)
        self.account2 = Account.objects.create(balance=1000, user=self.user2)
        self.account3 = Account.objects.create(balance=1000, user=self.user2)
        self.account4 = Account.objects.create(balance=1000, user=self.user3)


    # @patch('transactions.views.send_mail', lambda:print('mail sent'))
    def test_correct_create_transaction(self):
        # user1 = User.objects.create_user(username='user1', password='12345')
        # user2 = User.objects.create_user(username='user2', password='12345')
        # account1 = Account.objects.create(balance=1000, user=user1)
        # account2 = Account.objects.create(balance=1000, user=user2)
        # account3 = Account.objects.create(balance=1000, user=user2)
        from_accounts = self.user2.account_set.all()
        amount = 200
        transaction = Transaction.create_transaction(self.account1, from_accounts, amount)
        self.assertQuerysetEqual(transaction.from_accounts.all(), from_accounts, ordered=False)
        self.assertEqual(transaction.to_account, self.account1)
        self.assertEqual(self.account1.balance, 1200)
        self.account2.refresh_from_db()
        self.assertEqual(self.account2.balance, 900)
        self.account3.refresh_from_db()
        self.assertEqual(self.account3.balance, 900)

    
    def test_incorrect_create_transaction(self):
        # user1 = User.objects.create_user(username='user1', password='12345')
        # user2 = User.objects.create_user(username='user2', password='12345')
        # account1 = Account.objects.create(balance=1000, user=user1)
        # account2 = Account.objects.create(balance=100, user=user2)
        # account3 = Account.objects.create(balance=100, user=user2)
        from_accounts = self.user2.account_set.all()
        amount = 500
        self.assertRaises(ValueError, Transaction.create_transaction, self.account1, from_accounts, amount)


    def test_login(self):
        # c = Client()
        response = self.c.post('/login/', {'username': 'user1', 'password': '12345'})
        self.assertEqual(response.status_code, 200)
        
    
    def test_transaction_url(self):
        c = Client()
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')
        user3 = User.objects.create_user(username='user3', password='12345')
        account1 = Account.objects.create(balance=1000, user=user1)
        account2 = Account.objects.create(balance=1000, user=user2)
        account3 = Account.objects.create(balance=1000, user=user2)
        account4 = Account.objects.create(balance=1000, user=user3)
        from_accounts = user2.account_set.all()
        amount = 200
        transaction1:Transaction = Transaction.create_transaction(account1, from_accounts, amount)
        from_accounts = user1.account_set.all()
        amount = 300
        transaction2:Transaction = Transaction.create_transaction(account2, from_accounts, amount)
        from_accounts = user1.account_set.all()
        amount = 400
        transaction3:Transaction = Transaction.create_transaction(account4, from_accounts, amount)
        from_accounts = user2.account_set.all()
        amount = 500
        transaction4:Transaction = Transaction.create_transaction(account4, from_accounts, amount)

        c.login(username='user1', password='12345')
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction.html')
        self.assertInHTML(str(transaction1.id), response.content.decode())
        self.assertInHTML(f'<td>{float(transaction1.amount)}</td>', response.content.decode())
        self.assertContains(response, str(transaction1.date_time.strftime('%d.%m.%Y %H:%M')))
        self.assertIn(transaction1, response.context['filter'])
        self.assertIn(transaction2, response.context['filter'])
        self.assertIn(transaction3, response.context['filter'])
        self.assertNotIn(transaction4, response.context['filter'])


@pytest.fixture(scope='function')
def users(django_db_blocker):
    with django_db_blocker.unblock(): 
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')
        user3 = User.objects.create_user(username='user3', password='12345')
    return [user1, user2, user3]


@pytest.fixture(autouse=True)
def accounts(django_db_blocker, users):
    with django_db_blocker.unblock():
        account1 = Account.objects.create(balance=1000, user=users[0])
        account2 = Account.objects.create(balance=1000, user=users[1])
        account3 = Account.objects.create(balance=1000, user=users[2])
    return [account1, account2, account3]



@pytest.fixture(autouse=True)
def transactions(django_db_blocker, users):
    user1 = users[0]
    user2 = users[1]
    with django_db_blocker.unblock(): 
        transaction_list = []
        for account in user2.account_set.all():
            from_accounts = user1.account_set.all()
            amount = 200
            transaction1:Transaction = Transaction.create_transaction(account, from_accounts, amount)
            transaction_list.append(transaction1)
    return transaction_list

@pytest.mark.slow
# @pytest.mark.parametrized('transaction', self.transactions())
def test_cancel(db, transactions):
    for transaction in transactions:
        transaction.cancel()
        transaction.refresh_from_db()
        assert transaction.is_cancelled == True
        accounts = Account.objects.all()
        for account in accounts:
            assert account.balance == 1000


def generate_data():
    balances = [
        [
            1000, 200, 200
        ]
        , [
            0, 0, 0
        ]
        , [
            100, 1000, 1000
        ]
    ]
    amounts = [500, 700, 101]
    results = [pytest.raises(ValueError), pytest.raises(ValueError), None]
    for i in range(len(balances)):
        yield balances[i], amounts[i], results[i]

# @pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('balances, amount, expected_result', generate_data(), indirect=['balances', 'amount', 'expected_result'])
def test_conditional_transactions(django_db_blocker, users, balances, amount, expected_result):
    with django_db_blocker.unblock():
        user1 = users[0]
        user2 = users[1]
        account1 = Account.objects.create(balance=balances[0], user=user1)
        account2 = Account.objects.create(balance=balances[1], user=user1)
        account3 = Account.objects.create(balance=balances[2], user=user2)
        with expected_result:
            Transaction.create_transaction(account3, [account1, account2], amount)


# def test_create_transaction_with_mock():






