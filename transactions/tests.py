from django.test import TestCase, Client

from transactions.views import create_transaction
from .models import Account, Transaction
from django.contrib.auth.models import User

class TransactionTestCase(TestCase):
    def test_correct_create_transaction(self):
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')
        account1 = Account.objects.create(balance=1000, user=user1)
        account2 = Account.objects.create(balance=1000, user=user2)
        account3 = Account.objects.create(balance=1000, user=user2)
        from_accounts = user2.account_set.all()
        amount = 200
        transaction = Transaction.create_transaction(account1, from_accounts, amount)
        self.assertQuerysetEqual(transaction.from_accounts.all(), from_accounts, ordered=False)
        self.assertEqual(transaction.to_account, account1)
        self.assertEqual(account1.balance, 1200)
        account2.refresh_from_db()
        self.assertEqual(account2.balance, 900)
        account3.refresh_from_db()
        self.assertEqual(account3.balance, 900)

    
    def test_incorrect_create_transaction(self):
        #недостаточно средств - исключение assertRaises
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='12345')
        account1 = Account.objects.create(balance=1000, user=user1)
        account2 = Account.objects.create(balance=100, user=user2)
        account3 = Account.objects.create(balance=100, user=user2)
        from_accounts = user2.account_set.all()
        amount = 500
        self.assertRaises(ValueError, Transaction.create_transaction, account1, from_accounts, amount)


    def test_login(self):
        c = Client()
        response = c.post('/login/', {'username': 'user1', 'password': '12345'})
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
        # post транзакцию amount правильно списан (со всех счетов нужное количество) + setUp, tearDown

