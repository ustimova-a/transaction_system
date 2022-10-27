from django.urls import path, include
from . import views

urlpatterns = [
    # path('', views.transaction, name='transaction'),
    path('', views.TransactionView.as_view(), name='transaction'),
    # path('account/<int:account_id>/', views.account, name='account'),
    path('account/<int:account_id>/', views.AccountView.as_view(), name='account'),
    path('cancel/', views.cancel_transaction, name='cancel_transaction'),
    path('test/', views.test, name='test'),
    path('user_transactions/', views.TransactionListView.as_view()),
    path('api/', include([
        path('account/<int:pk>/', views.AccountAPIView.as_view(), name='account_detail')
    ])),
]