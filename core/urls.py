from django.urls import path
from .views import (
    OrganizationCreateView, 
    UserRegisterView, 
    PlanListView, 
    SubscribeView,
    MyUsersView,
    DownloadInvoiceView,
    AdminDashboardView,
    StripeWebhookView,
    CancelSubscriptionView,
    UpdateSubscriptionView,
    UserUpdateView,
    SendSubscriptionCreatedEmailView,
    SendPaymentSuccessEmailView,
    UserDeleteView
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
    path('subscription/cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('subscription/update/', UpdateSubscriptionView.as_view(), name='update-subscription'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('email/subscription-created/', SendSubscriptionCreatedEmailView.as_view(), name='email-subscription-created'),
    path('email/payment-success/', SendPaymentSuccessEmailView.as_view(), name='email-payment-success'),
]

