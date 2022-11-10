from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('accounts', views.AccoutViewSet, basename='accounts')

urlpatterns = [
    # path('', views.transaction, name='transaction'),
    path('', views.TransactionView.as_view(), name='transaction'),
    # path('account/<int:account_id>/', views.account, name='account'),
    path('account/<int:account_id>/', views.AccountView.as_view(), name='account'),
    path('cancel/', views.cancel_transaction, name='cancel_transaction'),
    path('test/', views.test, name='test'),
    path('user_transactions/', views.TransactionListView.as_view()),
    path('api/', include([
        path('', include('rest_framework.urls')),
        path('', include(router.urls)),
        path('account/<int:pk>/', views.AccountAPIView.as_view(), name='account_detail'),
        path('get_token/', views.ObtainToken.as_view(), name='obtain_token')
    ])),
]