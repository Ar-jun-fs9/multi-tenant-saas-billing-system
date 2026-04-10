from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, OrganizationSerializer
from .models import Plan, Subscription, Organization, User
from .serializers import PlanSerializer, SubscriptionSerializer
import stripe
from django.conf import settings
from django.core.mail import send_mail
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from io import BytesIO
import os
import requests
from .stripe_utils import stripe


def Home(request):
    return HttpResponse("Welcome to the Multi-Tenant SaaS Billing System!")


class OrganizationCreateView(generics.CreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        organization = serializer.save()

        try:
            stripe_customer = stripe.Customer.create(
                name=organization.name, metadata={"organization_id": organization.id}
            )

            organization.stripe_customer_id = stripe_customer.id
            organization.save()

            print("✅ Stripe customer created:", stripe_customer.id)
            print("🏢 Organization updated with Stripe ID")

        except Exception as e:
            print("❌ Stripe customer creation FAILED:", str(e))


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        org = request.user.organization

        if not org:
            return Response({"error": "User has no organization"}, status=400)

        plan_id = request.data.get("plan_id")

        if not plan_id:
            return Response({"error": "plan_id is required"}, status=400)

        # 🔍 Validate plan
        try:
            plan = Plan.objects.get(id=int(plan_id))
        except (Plan.DoesNotExist, ValueError):
            return Response({"error": "Invalid plan_id"}, status=404)

        # 🔥 Ensure Stripe customer exists
        try:
            if not org.stripe_customer_id:
                customer = stripe.Customer.create(
                    name=org.name,
                    email=request.user.email if request.user.email else None,
                )
                org.stripe_customer_id = customer.id
                org.save()
        except Exception as e:
            return Response(
                {"error": "Failed to create Stripe customer", "details": str(e)},
                status=500,
            )

        # 💳 Create Stripe Checkout Session
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=org.stripe_customer_id,
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": plan.stripe_price_id,
                        "quantity": 1,
                    }
                ],
                success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:8000/cancel",
            )

            return Response({"checkout_url": checkout_session.url})

        except Exception as e:
            return Response(
                {"error": "Stripe checkout session creation failed", "details": str(e)},
                status=500,
            )


class MyUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "User has no organization"}, status=400)
        users = User.objects.filter(organization=org)
        data = [{"username": u.username, "email": u.email} for u in users]
        return Response(data)


class DownloadInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subscription_id):
        try:
            subscription = Subscription.objects.get(
                id=subscription_id, organization=request.user.organization
            )
        except Subscription.DoesNotExist:
            return Response({"error": "Subscription not found"}, status=404)

        template = "invoice_template.html"
        try:
            html = render_to_string(template, {"subscription": subscription})
        except:
            html = f"""
            <h2>Invoice for {subscription.organization.name}</h2>
            <p>Plan: {subscription.plan.name}</p>
            <p>Amount: ${subscription.plan.price}</p>
            <p>Status: {subscription.status}</p>
            <p>Date: {subscription.start_date}</p>
            """

        result = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=result)
        if pisa_status.err:
            return Response({"error": "PDF generation failed"}, status=500)

        return HttpResponse(result.getvalue(), content_type="application/pdf")


class AdminDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SubscriptionSerializer

    def get_object(self):
        return self.request.user.organization

    def retrieve(self, request, *args, **kwargs):
        org = request.user.organization
        subscriptions = Subscription.objects.filter(organization=org)
        data = {
            "id": org.id,
            "name": org.name,
            "created_at": org.created_at,
            "subscriptions": [
                {"plan": s.plan.name, "status": s.status, "start_date": s.start_date}
                for s in subscriptions
            ],
        }
        return Response(data)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except Exception as e:
            print("❌ SIGNATURE ERROR:", str(e))
            return Response(status=400)

        print("🔥 EVENT:", event["type"])

        # =====================================================
        # ONLY RELIABLE EVENT FOR SUBSCRIPTIONS
        # =====================================================
        if event["type"] == "customer.subscription.created":
            sub = event["data"]["object"]

            customer_id = sub["customer"]
            subscription_id = sub["id"]
            status = sub["status"]

            print("👤 CUSTOMER:", customer_id)
            print("📦 SUB:", subscription_id)

            try:
                org = Organization.objects.get(stripe_customer_id=customer_id)

                # Get price → plan mapping
                price_id = sub["items"]["data"][0]["price"]["id"]
                plan = Plan.objects.get(stripe_price_id=price_id)

                subscription, created = Subscription.objects.update_or_create(
                    stripe_subscription_id=subscription_id,
                    defaults={"organization": org, "plan": plan, "status": status},
                )

                print("✅ SUBSCRIPTION SAVED:", subscription.id)

            except Exception as e:
                print("❌ DB ERROR:", str(e))

        # Optional safety updates
        elif event["type"] == "invoice.payment_succeeded":
            sub_id = event["data"]["object"]["subscription"]
            Subscription.objects.filter(stripe_subscription_id=sub_id).update(
                status="active"
            )

        elif event["type"] == "invoice.payment_failed":
            sub_id = event["data"]["object"]["subscription"]
            Subscription.objects.filter(stripe_subscription_id=sub_id).update(
                status="past_due"
            )

        return Response(status=200)
