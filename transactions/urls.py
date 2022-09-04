from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction, name='transaction'),
    path('filter/', views.filter_transactions, name='filter_transactions'),
    path('account/<int:account_id>/', views.account, name='account'),
    path('cancel/', views.cancel_transaction, name='cancel_transaction'),
    path('test/', views.test, name='test'),
]