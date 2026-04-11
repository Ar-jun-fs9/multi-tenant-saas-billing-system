<div align="center">

# Multi-Tenant SaaS Billing API

<p align="center">
  <a href="https://multi-tenant-saas-billing-system.onrender.com/">
    🌐 Live Demo
  </a>
</p>

<p align="center">
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django-Backend-092E20?style=flat&logo=django&logoColor=white" alt="Django">
  </a>
  <a href="https://www.django-rest-framework.org/">
    <img src="https://img.shields.io/badge/DRF-API-ff1709?style=flat&logo=django&logoColor=white" alt="DRF">
  </a>
  <a href="https://stripe.com/">
    <img src="https://img.shields.io/badge/Stripe-Payments-635BFF?style=flat&logo=stripe&logoColor=white" alt="Stripe">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-Database-336791?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>
</p>

</div>

A stable and reliable Django REST API for multi-tenant SaaS subscription billing with Stripe integration.

**[Live Demo](https://multi-tenant-saas-billing-system.onrender.com/)** · **[Local Development](#local-setup)** · **[API Documentation](#api-endpoints)** · **[Testing](#testing)**

---

## Quick Start

### Live Demo (No Setup Required)

| Deployment | URL                                         | Description                    |
| ---------- | ------------------------------------------- | ---------------------------- |
| **Render** | https://multi-tenant-saas-billing-system.onrender.com/ | Live production deployment     |
| **Local**  | http://127.0.0.1:8000/                      | Local development server    |

```bash
# Test the live API - Create organization
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/organization/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'

# Register user
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/user/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass", "email": "user@test.com", "organization": 1}'

# Get JWT token
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

---

## Screenshots

The following images show the Multi-Tenant SaaS Billing API in action from organization setup to active subscription.

### Step 1-2: Organization & User Registration

| ![organization1](assets/oragnization%20create_1.png) | ![user_register](assets/user%20register_2.png) |
| ------------------------------------------- | --------------------------------------- |
| Create new organization              | Register user with role              |

---

### Step 3-4: Authentication & Plans

| ![token](assets/token_3.png) | ![token_refresh](assets/token%20refresh_4.png) |
| --------------------------- | -------------------------------------- |
| Get JWT access token         | Refresh token endpoint          |

| ![plans](assets/plans_5.png) |
| -------------------------- |
| Browse subscription plans       |

---

### Step 5-6: Subscribe & Payment

| ![subscribe](assets/subscribe_6.png) | ![stripe](assets/stripe_7.png) |
| ------------------------------ | ---------------------------- |
| Create checkout session        | Stripe checkout page         |

| ![pay](assets/pay_8.png) |
| ---------------------- |
| Complete payment        |

---

### Step 7-8: Confirmation & Subscription

| ![stripe_dashboard](assets/stripe_dashboard_9.png) | ![stripe_trans](assets/stripe_trans_10.png) |
| -------------------------------------------- | ----------------------------------- |
| Transaction history           | Payment details             |

| ![subscription](assets/subscription_11.png) |
| --------------------------------------- |
| Active subscription status               |

---

## Live Demo vs Local

### Available Deployments

| Environment       | Base URL                                   | Best For                                |
| ----------------- | ------------------------------------------ | --------------------------------------- |
| **Render (Live)** | https://multi-tenant-saas-billing-system.onrender.com | Quick testing, demos, sharing with team |
| **Localhost**     | http://127.0.0.1:8000                      | Development, debugging, custom changes  |

### Testing Each Version

**Live Demo (Render):**

```bash
# Create organization
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/organization/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Company"}'

# Register user
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/user/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass", "organization": 1}'

# Get token
curl -X POST https://multi-tenant-saas-billing-system.onrender.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# List plans
curl -X GET https://multi-tenant-saas-billing-system.onrender.com/api/plans/
```

**Local Development:**

```bash
# Start server
python manage.py runserver

# Create organization
curl -X POST http://127.0.0.1:8000/api/organization/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Company"}'

# Access admin
http://127.0.0.1:8000/admin
```

### When to Use Which?

- **Use Live Demo when:** You want to quickly test the API without any setup, share with teammates, or integrate with external services
- **Use Local when:** You need to modify code, debug issues, add features, or test with your own database

---

## What is this project?

This project provides a complete billing solution for SaaS companies to manage subscriptions, organizations, and payments. Built with Django REST Framework and Stripe, it handles the entire billing lifecycle from organization registration to invoice generation.

## Features

### Core Functionality
- **Multi-Tenancy** - Complete data isolation between organizations
- **Organization Management** - Register and manage multiple tenants
- **User Management** - Role-based access (Admin/Member)
- **Subscription Plans** - Create and manage pricing plans
- **Stripe Integration** - Checkout sessions, webhooks, and recurring billing
- **Invoice Generation** - Download PDF invoices
- **Email Notifications** - Automated payment and subscription emails
- **JWT Authentication** - Secure token-based API access

### API Endpoints

#### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/success/` | Payment success page |
| GET | `/cancel/` | Payment cancel page |
| POST | `/api/organization/register/` | Create organization |
| POST | `/api/user/register/` | Register user |
| POST | `/api/token/` | Get JWT token |
| POST | `/api/token/refresh/` | Refresh JWT token |
| POST | `/api/stripe/webhook/` | Stripe webhook handler |

#### Protected Endpoints (JWT Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plans/` | List subscription plans |
| POST | `/api/subscribe/` | Create Stripe checkout session |
| POST | `/api/subscription/cancel/` | Cancel subscription |
| POST | `/api/subscription/update/` | Upgrade/downgrade plan |
| GET | `/api/my-users/` | List organization users |
| GET | `/api/invoice/{id}/` | Download PDF invoice |
| GET | `/api/admin-dashboard/` | Admin dashboard |
| PATCH | `/api/user/update/` | Update user profile |
| DELETE | `/api/user/delete/` | Soft delete user |
| POST | `/api/email/subscription-created/` | Send subscription confirmation email |
| POST | `/api/email/payment-success/` | Send payment success email |

## Tech Stack

- **Backend**: Django 6.0.3
- **API**: Django REST Framework 3.17.1
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: JWT (rest_framework_simplejwt)
- **Payments**: Stripe
- **PDF**: xhtml2pdf

## Project Structure

```
multi_tenant_saas_billing/
├── manage.py
├── multi_tenant_saas_billing/
│   ├── settings.py          # Django settings
│   ├── urls.py               # Root URL config
│   └── wsgi.py
├── core/
│   ├── models.py             # Organization, User, Plan, Subscription
│   ├── views.py              # API views (16 endpoints)
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # API URL patterns
│   ├── admin.py              # Django admin
│   ├── stripe_utils.py       # Stripe configuration
│   └── migrations/           # Database migrations
├── templates/
│   ├── homepage.html         # Landing page
│   └── payment.html          # Payment success/cancel
├── .env                      # Environment variables
├── test_cases.md             # API testing guide
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (or Supabase)
- Stripe Account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ar-jun-fs9/multi-tenant-saas-billing-system.git
   cd multi-tenant-saas-billing-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv saasvenv
   saasvenv\Scripts\activate  # Windows
   # OR
   source saasvenv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install requirements.txt
   ```

4. **Configure environment variables**

   Create `.env` file:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/dbname
   STRIPE_API_KEY=sk_test_...
   SECRET_KEY=your-secret-key
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@saasbilling.com
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

## Quick Start Guide

### 1. Create an Organization

```bash
curl -X POST http://localhost:8000/api/organization/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Company"}'
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/api/user/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123", "email": "john@company.com", "organization": 1}'
```

### 3. Get JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123"}'
```

### 4. List Plans

```bash
curl -X GET http://localhost:8000/api/plans/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Subscribe to a Plan

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"plan_id": 1}'
```

## Database Models

### Organization
- `name` - Company name
- `stripe_customer_id` - Linked Stripe customer
- `created_at` - Creation timestamp

### User (extends AbstractUser)
- `organization` - ForeignKey to Organization
- `role` - 'admin' or 'member'

### Plan
- `name` - Plan name (e.g., "Basic", "Pro")
- `stripe_price_id` - Stripe price ID
- `price` - Monthly price in USD
- `description` - Plan details

### Subscription
- `organization` - ForeignKey to Organization
- `plan` - ForeignKey to Plan
- `stripe_subscription_id` - Stripe subscription ID
- `status` - 'active', 'canceled', 'past_due'
- `start_date`, `end_date`

## Multi-Tenancy

This API enforces data isolation:

- Users can only access data within their organization
- Subscriptions are per-organization (company-level billing)
- Each organization has its own Stripe customer
- All queries are filtered by organization ID

## Testing

See `test_cases.md` for comprehensive API testing including:

- Step-by-step workflow testing
- Request/response examples
- Error handling scenarios
- Postman collection setup
- Rate limit testing

## Rate Limiting

The API includes built-in rate limiting:

| Scope | Limit |
|-------|-------|
| Anonymous | 100/day |
| Authenticated | 1000/day |
| Login attempts | 10/min |

## Stripe Configuration

### 1. Create Stripe Products and Prices

In your Stripe Dashboard:
1. Create products (Basic, Pro, Enterprise)
2. Create recurring prices for each product
3. Copy the `price_xxx` IDs

### 2. Add Plans to Database

```python
# Via Django admin or management command
Plan.objects.create(
    name="Pro",
    stripe_price_id="price_xxx",
    price=29.99,
    description="Pro plan with all features"
)
```

### 3. Configure Webhooks

Point Stripe webhooks to:
```
http://localhost:8000/api/stripe/webhook/
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `STRIPE_API_KEY` | Stripe secret key | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `EMAIL_HOST_USER` | SMTP username | No |
| `EMAIL_HOST_PASSWORD` | SMTP password | No |
| `DEFAULT_FROM_EMAIL` | From email address | No |

## Future Enhancements

- Trial periods
- Usage-based billing
- Proration handling
- Payment retry logic
- Additional role permissions
- Analytics dashboard

## License

MIT License


