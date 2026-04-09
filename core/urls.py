from django.urls import path
from .views import (
    OrganizationCreateView, 
    UserRegisterView, 
    PlanListView, 
    SubscribeView,
    MyUsersView,
    DownloadInvoiceView,
    AdminDashboardView,
    StripeWebhookView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('organization/register/', OrganizationCreateView.as_view(), name='organization-register'),
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('my-users/', MyUsersView.as_view(), name='my-users'),
    path('invoice/<int:subscription_id>/', DownloadInvoiceView.as_view(), name='download-invoice'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]

