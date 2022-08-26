from django.urls import path
from . import views

urlpatterns = [
    path('filter/', views.filter_transactions, name='filter_transactions'),
    path('account/', views.account, name='account'),
]