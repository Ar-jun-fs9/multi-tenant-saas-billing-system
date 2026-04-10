"""
URL configuration for multi_tenant_saas_billing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from core.models import Subscription, Plan, Organization

def home(request):
    return render(request, 'homepage.html')

def success(request):
    session_id = request.GET.get('session_id')
    print(f"SUCCESS VIEW - session_id: {session_id}")
    
    sub_status = 'active'
    sub_plan = 'Subscription'
    sub_amount = '$0.00'
    
    if session_id:
        try:
            from core.stripe_utils import stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            # print(f"Checkout session: {checkout_session.id}, payment_status: {checkout_session.payment_status}")
            
            if checkout_session.payment_status == 'paid':
                sub_id = checkout_session.subscription
                # print(f"Subscription ID from checkout: {sub_id}")
                
                if sub_id:
                    db_sub = Subscription.objects.filter(stripe_subscription_id=sub_id).first()
                    if db_sub:
                        sub_status = db_sub.status
                        sub_plan = db_sub.plan.name
                        sub_amount = f"${db_sub.plan.price:.2f}"
                        print(f"Found in DB: {db_sub.plan.name}")
                    else:
                        print("Not found in DB, trying Stripe API...")
                        stripe_sub = stripe.Subscription.retrieve(sub_id)
                        price_id = stripe_sub['items']['data'][0]['price']['id']
                        db_plan = Plan.objects.filter(stripe_price_id=price_id).first()
                        
                        if db_plan:
                            sub_plan = db_plan.name
                            sub_amount = f"${db_plan.price:.2f}"
                            try:
                                customer_id = checkout_session.customer
                                org = Organization.objects.filter(stripe_customer_id=customer_id).first()
                                if org:
                                    new_sub, created = Subscription.objects.update_or_create(
                                        stripe_subscription_id=sub_id,
                                        defaults={
                                            'organization': org,
                                            'plan': db_plan,
                                            'status': 'active'
                                        }
                                    )
                                    print(f"Subscription SAVED to DB: {new_sub.id}")
                            except Exception as save_err:
                                print(f"Could not save: {save_err}")
                            print(f"Found via Stripe: {db_plan.name}")
                        else:
                            print(f"Price ID from Stripe: {price_id}")
        except Exception as e:
            print(f"ERROR in success view: {e}")
            import traceback
            traceback.print_exc()
    
    context = {
        'success': True,
        'sub_status': sub_status,
        'sub_plan': sub_plan,
        'sub_amount': sub_amount,
    }
    # print(f"Context: {context}")
    
    return render(request, 'payment.html', context)

def cancel(request):
    return render(request, 'payment.html', {'success': False})

urlpatterns = [
    # path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('', home, name='home'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
]


