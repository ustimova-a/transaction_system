from django.test import TestCase
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
        #недостаточно средств - исключение assertRaises, +Client (inhtml)
        pass
