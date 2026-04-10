<div align=center>

# Multi-Tenant SaaS Billing API - Test Cases

</div>
## Overview

This document provides a complete test plan for testing the Multi-Tenant SaaS Billing API using Postman or similar tools.

### Test Environment
- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

### Test Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        END-TO-END TEST WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1:     GET /                  → Verify API is running
Step 2:     POST /api/organization/  → Create Organization + Stripe Customer
Step 3:     POST /api/user/register → Create User in Organization
Step 4:     POST /api/token/       → Login (Get JWT Token)
Step 5:     POST /api/token/refresh → Refresh JWT Token
Step 6:     GET /api/plans/       → View Available Plans
Step 7:     POST /api/subscribe/   → Create Stripe Checkout Session
Step 8:     (Manual Payment)     → User completes payment on Stripe
Step 9:     POST /api/stripe/webhook/ → Handle Subscription Events
Step 10:    GET /api/my-users/      → View Organization Users
Step 11:    GET /api/invoice/{id}/ → Download Invoice PDF
Step 12:    GET /api/admin-dashboard/ → View Organization Stats
```

---

## Step 1: Verify API is Running

### Endpoint: GET /

**Purpose**: Verify the API server is running and responsive.

**Request**:
```http
GET http://localhost:8000/
```

**Success Response**:
```
200 OK

Welcome to the Multi-Tenant SaaS Billing System!
```

**What User CAN Do**:
- Verify the server is online
- Check API health

**What User CANNOT Do**:
- Access any protected endpoints
- Modify any data

**Important Rules**:
- This is a public endpoint (no authentication required)
- First check if API is responding before testing other endpoints

---

## Step 2: Create Organization

### Endpoint: POST /api/organization/register/

**Purpose**: Create a new company/organization in the system. This automatically creates a Stripe Customer for the organization.

**Request**:
```http
POST http://localhost:8000/api/organization/register/
Content-Type: application/json

{
    "name": "TechCorp Inc."
}
```

**Success Response** (201 Created):
```json
{
    "id": 1,
    "name": "TechCorp Inc."
}
```

**Failure Scenarios**:

1. **Missing name** (400 Bad Request):
```json
{
    "name": ["This field is required."]
}
```

2. **Empty name** (400 Bad Request):
```json
{
    "name": ["This field is required."]
}
```

**What User CAN Do**:
- Create a new organization
- The organization is automatically linked to a Stripe Customer

**What User CANNOT Do**:
- Create duplicate organization names (allowed, but not recommended)
- Skip providing organization name

**Important Rules**:
- No authentication required to create organization
- Stripe customer is created automatically in background
- This is typically the FIRST step in the entire workflow

**Test Data**:
- Valid: "TechCorp Inc.", "StartupXYZ Ltd.", "Acme Corporation"
- Invalid: "" (empty string), null

---

## Step 3: Register User

### Endpoint: POST /api/user/register/

**Purpose**: Register a new user and associate them with an organization.

**Request**:
```http
POST http://localhost:8000/api/user/register/
Content-Type: application/json

{
    "username": "john_smith",
    "email": "john@techcorp.com",
    "password": "SecurePass123!",
    "organization": 1
}
```

**Success Response** (201 Created):
```json
{
    "id": 1,
    "username": "john_smith",
    "email": "john@techcorp.com",
    "organization": 1
}
```

**Failure Scenarios**:

1. **Missing required fields** (400 Bad Request):
```json
{
    "username": ["This field is required."],
    "password": ["This field is required."]
}
```

2. **Invalid organization ID** (400 Bad Request):
```json
{
    "non_field_errors": ["Invalid pk \"999\" - object does not exist."]
}
```

3. **Duplicate username** (400 Bad Request):
```json
{
    "username": ["A user with that username already exists."]
}
```

**What User CAN Do**:
- Create a new user associated with their organization
- Set password for the user

**What User CANNOT Do**:
- Create a user without an organization (organization field required)
- Create users for other organizations (must use valid org ID)
- Skip password field

**Important Rules**:
- No authentication required to register user
- User must be linked to a valid organization
- Password is hashed before storage

**Test Data**:
- Valid org ID: 1, 2, 3 (existing in DB)
- Invalid org ID: 999, 0, -1

---

## Step 4: Login (Get JWT Token)

### Endpoint: POST /api/token/

**Purpose**: Authenticate user and obtain JWT access token for protected endpoints.

**Request**:
```http
POST http://localhost:8000/api/token/
Content-Type: application/json

{
    "username": "john_smith",
    "password": "SecurePass123!"
}
```

**Success Response** (200 OK):
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Failure Scenarios**:

1. **Invalid credentials** (401 Unauthorized):
```json
{
    "detail": "No active account found with the given credentials."
}
```

2. **Wrong password** (401 Unauthorized):
```json
{
    "detail": "No active account found with the given credentials."
}
```

3. **Missing fields** (400 Bad Request):
```json
{
    "username": ["This field is required."],
    "password": ["This field is required."]
}
```

**What User CAN Do**:
- Authenticate with valid username and password
- Receive access and refresh tokens
- Use access token for protected endpoints

**What User CANNOT Do**:
- Login without valid credentials
- Use expired tokens (must refresh)

**Important Rules**:
- Returns two tokens: access (short-lived) and refresh (longer-lived)
- Access token needed for Authorization header
- Token format: `Authorization: Bearer <access_token>`

**Test Data**:
- Valid user: username "john_smith", password "SecurePass123!"
- Invalid: wrong username, wrong password

---

## Step 5: Refresh JWT Token

### Endpoint: POST /api/token/refresh/

**Purpose**: Obtain a new access token using the refresh token.

**Request**:
```http
POST http://localhost:8000/api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response** (200 OK):
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Failure Scenarios**:

1. **Invalid/expired refresh token** (401 Unauthorized):
```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```

2. **Missing refresh field** (400 Bad Request):
```json
{
    "refresh": ["This field is required."]
}
```

**What User CAN Do**:
- Get new access token without re-authenticating
- Continue using the API with new token

**What User CANNOT Do**:
- Use expired refresh token indefinitely
- Skip providing refresh token

**Important Rules**:
- Requires valid refresh token from Step 4
- Access tokens expire; refresh to get new one

---

## Step 6: List Subscription Plans

### Endpoint: GET /api/plans/

**Purpose**: View all available subscription plans that organizations can subscribe to.

**Request**:
```http
GET http://localhost:8000/api/plans/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
[
    {
        "id": 1,
        "name": "Basic",
        "stripe_price_id": "price_1234567890",
        "price": 10.0,
        "description": "Up to 10 users"
    },
    {
        "id": 2,
        "name": "Pro",
        "stripe_price_id": "price_0987654321",
        "price": 30.0,
        "description": "Unlimited users"
    },
    {
        "id": 3,
        "name": "Enterprise",
        "stripe_price_id": "price_abcdefghi",
        "price": 100.0,
        "description": "Priority support"
    }
]
```

**Failure Scenarios**:

1. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

2. **Invalid token** (401 Unauthorized):
```json
{
    "detail": "Invalid token."
}
```

**What User CAN Do**:
- View all available plans
- See plan names, prices, and Stripe price IDs

**What User CANNOT Do**:
- Access without authentication
- Modify plans (admin only via Django admin)

**Important Rules**:
- Authentication required (JWT token)
- Plans are managed in admin or via database

**Test Data**:
- Valid: Any valid JWT token from Step 4
- Invalid: Invalid token, expired token, no token

---

## Step 7: Subscribe to Plan

### Endpoint: POST /api/subscribe/

**Purpose**: Create a Stripe Checkout Session for the organization to subscribe to a plan.

**Request**:
```http
POST http://localhost:8000/api/subscribe/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "plan_id": 2
}
```

**Success Response** (200 OK):
```json
{
    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_..."
}
```

**Failure Scenarios**:

1. **User has no organization** (400 Bad Request):
```json
{
    "error": "User has no organization"
}
```

2. **Missing plan_id** (400 Bad Request):
```json
{
    "error": "plan_id is required"
}
```

3. **Invalid plan_id** (404 Not Found):
```json
{
    "error": "Invalid plan_id"
}
```

4. **No Stripe customer** (500 Internal Server Error):
```json
{
    "error": "Failed to create Stripe customer",
    "details": "..."
}
```

**What User CAN Do**:
- Create checkout session for their organization's subscription
- Redirect user to Stripe checkout page
- Accept payment via Stripe hosted page

**What User CANNOT Do**:
- Subscribe without being part of an organization
- Subscribe without a valid plan
- Subscribe another organization's users

**Important Rules**:
- Authentication required
- Multi-tenancy: Users can only create subscription for their own organization
- Must have Stripe customer ID (created in Step 2 or during subscribe)

**Test Data**:
- Valid plan_id: 1, 2, 3
- Invalid plan_id: 999, 0, "abc"

---

## Step 8: Complete Payment (Manual)

### Endpoint: External - Stripe Checkout

**Purpose**: User completes payment on Stripe's hosted checkout page.

**Process**:
1. User is redirected to `checkout_url` from Step 7
2. User enters card details on Stripe's secure page
3. User completes payment
4. Stripe redirects to success or cancel URL

**Success Redirect**:
```
http://localhost:8000/success?session_id=<stripe_session_id>
```

**Cancel Redirect**:
```
http://localhost:8000/cancel
```

**What User CAN Do**:
- Complete payment securely on Stripe
- Enter card details
- Receive confirmation

**What User CANNOT Do**:
- Modify payment amount
- Skip payment

**Important Rules**:
- This is handled by Stripe, not the API
- After payment, webhook notifies the API (Step 9)

---

## Step 9: Handle Stripe Webhook

### Endpoint: POST /api/stripe/webhook/

**Purpose**: Handle Stripe webhook events to create/update subscriptions in the database.

**Request**:
```http
POST http://localhost:8000/api/stripe/webhook/
Content-Type: application/json
Stripe-Signature: <signature>

{
    "id": "evt_...",
    "type": "customer.subscription.created",
    "data": {
        "object": {
            "id": "sub_123",
            "customer": "cus_ABC123",
            "status": "active",
            "items": {
                "data": [
                    {
                        "price": {
                            "id": "price_0987654321"
                        }
                    }
                ]
            }
        }
    }
}
```

**Success Response** (200 OK):
```json
{}
```

**Processed Events**:
- `customer.subscription.created` → Creates Subscription record
- `invoice.payment_succeeded` → Updates status to "active"
- `invoice.payment_failed` → Updates status to "past_due"

**What User CAN Do**:
- Receive webhook events from Stripe
- Automatically create subscriptions
- Update subscription status

**What User CANNOT Do**:
- Skip webhook processing
- Manually create subscriptions without payment

**Important Rules**:
- No authentication (uses Stripe signature verification)
- Requires STRIPE_WEBHOOK_SECRET environment variable
- Maps Stripe customer to Organization via stripe_customer_id

**Test Data**:
- Valid customer ID: Must match organization in DB
- Valid price ID: Must match plan in DB

---

## Step 10: List Organization Users

### Endpoint: GET /api/my-users/

**Purpose**: View all users belong to the authenticated user's organization.

**Request**:
```http
GET http://localhost:8000/api/my-users/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
[
    {
        "username": "john_smith",
        "email": "john@techcorp.com"
    },
    {
        "username": "sarah_jones",
        "email": "sarah@techcorp.com"
    }
]
```

**Failure Scenarios**:

1. **User has no organization** (400 Bad Request):
```json
{
    "error": "User has no organization"
}
```

2. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**What User CAN Do**:
- View all users in their organization
- See usernames and emails of their colleagues

**What User CANNOT Do**:
- View users from other organizations
- Access without authentication
- View organization-less users

**Important Rules**:
- Authentication required
- Multi-tenancy: Only returns users from the authenticated user's organization
- This is a core security feature

**Test Data**:
- Expected: Users from organization 1 when logged in as org 1 user

---

## Step 11: Download Invoice

### Endpoint: GET /api/invoice/{subscription_id}/

**Purpose**: Download invoice PDF for a subscription.

**Request**:
```http
GET http://localhost:8000/api/invoice/1/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```pdf
Content-Type: application/pdf
Content-Disposition: attachment; filename="invoice_1.pdf"

<PDF binary content>
```

**Failure Scenarios**:

1. **Subscription not found** (404 Not Found):
```json
{
    "error": "Subscription not found"
}
```

2. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

3. **Accessing another organization's subscription** (404 Not Found):
```json
{
    "error": "Subscription not found"
}
```

**What User CAN Do**:
- Download invoice PDF for their organization's subscriptions
- View billing details (plan, amount, date, status)

**What User CANNOT Do**:
- Download invoices from other organizations
- Access without authentication
- Access non-existent subscriptions

**Important Rules**:
- Authentication required
- Multi-tenancy: Can only access own organization's subscriptions
- Returns PDF file, not JSON

**Test Data**:
- Valid subscription_id: 1, 2, 3 (belongs to user's org)
- Invalid subscription_id: 999, 0

---

## Step 12: Admin Dashboard

### Endpoint: GET /api/admin-dashboard/

**Purpose**: View organization statistics and subscription details.

**Request**:
```http
GET http://localhost:8000/api/admin-dashboard/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
    "id": 1,
    "name": "TechCorp Inc.",
    "created_at": "2026-04-10T10:00:00Z",
    "subscriptions": [
        {
            "plan": "Pro",
            "status": "active",
            "start_date": "2026-04-10T10:30:00Z"
        }
    ]
}
```

**Failure Scenarios**:

1. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

2. **User has no organization** (400 Bad Request):
```json
{
    "error": "User has no organization"
}
```

**What User CAN Do**:
- View their organization's subscription list
- See organization details and creation date
- Monitor subscription status

**What User CANNOT Do**:
- View other organizations' data
- Access without authentication
- View organization statistics without being in one

**Important Rules**:
- Authentication required
- Multi-tenancy: Only shows own organization's data
- Requires organization membership

---

## Payment Status Pages

### Success Page: GET /success/

**Purpose**: Displayed after successful payment on Stripe.

**Request**:
```http
GET http://localhost:8000/success?session_id=<session_id>
```

**Response** (200 OK):
```
Payment successful! Subscription will be activated shortly.
```

### Cancel Page: GET /cancel/

**Purpose**: Displayed if user cancels payment on Stripe.

**Request**:
```http
GET http://localhost:8000/cancel
```

**Response** (200 OK):
```
Payment cancelled!
```

---

## Testing Matrix

### Endpoint Authentication Matrix

| Endpoint | Auth Required | Admin Only |
|----------|--------------|-------------|
| GET / | No | No |
| POST /api/organization/register/ | No | No |
| POST /api/user/register/ | No | No |
| POST /api/token/ | No | No |
| POST /api/token/refresh/ | No | No |
| GET /api/plans/ | Yes | No |
| POST /api/subscribe/ | Yes | No |
| POST /api/stripe/webhook/ | No | No |
| GET /api/my-users/ | Yes | No |
| GET /api/invoice/{id}/ | Yes | No |
| GET /api/admin-dashboard/ | Yes | No |

### Error Response Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (client error) |
| 401 | Unauthorized (no/missing auth) |
| 404 | Not Found |
| 500 | Server Error |

---

## Postman Collection Variables

Set these variables in Postman to make testing easier:

```
{{base_url}} = http://localhost:8000
{{access_token}} = <paste from login response>
{{refresh_token}} = <paste from login response>
{{organization_id}} = 1
{{user_id}} = 1
{{plan_id}} = 2
{{subscription_id}} = 1
```

### Sample Test Order

1. **Organization Setup**:
   ```bash
   POST {{base_url}}/api/organization/register/
   Body: {"name": "Test Company"}
   ```

2. **User Registration**:
   ```bash
   POST {{base_url}}/api/user/register/
   Body: {"username": "testuser", "password": "Pass123!", "organization": {{organization_id}}, "email": "test@test.com"}
   ```

3. **Login**:
   ```bash
   POST {{base_url}}/api/token/
   Body: {"username": "testuser", "password": "Pass123!"}
   ```
   → Save `access` to {{access_token}}

4. **List Plans**:
   ```bash
   GET {{base_url}}/api/plans/
   Headers: Authorization: Bearer {{access_token}}
   ```

5. **Subscribe**:
   ```bash
   POST {{base_url}}/api/subscribe/
   Headers: Authorization: Bearer {{access_token}}
   Body: {"plan_id": {{plan_id}}}
   ```

6. **Check Users**:
   ```bash
   GET {{base_url}}/api/my-users/
   Headers: Authorization: Bearer {{access_token}}
   ```

7. **Download Invoice**:
   ```bash
   GET {{base_url}}/api/invoice/{{subscription_id}}/
   Headers: Authorization: Bearer {{access_token}}
   ```

---

---

## Currently Implemented Features

  **Implemented:**
- Organization registration with Stripe customer creation
- User registration with organization linking
- User roles (admin, member)
- JWT authentication (login + refresh)
- Plan listing (read-only via database)
- Stripe Checkout Session creation
- Stripe webhook handling (subscription events)
- Invoice PDF generation
- Admin dashboard (organization view)
- Multi-tenant data isolation
- Subscription cancel endpoint
- Subscription update endpoint (upgrade/downgrade)
- User profile update endpoint
- User delete endpoint (soft delete)
- Email notifications (subscription created, payment success)
- API rate limiting

---

## NEW: Step 13: Cancel Subscription

### Endpoint: POST /api/subscription/cancel/

**Purpose**: Cancel the organization's active subscription.

**Request**:
```http
POST http://localhost:8000/api/subscription/cancel/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
    "message": "Subscription cancelled successfully"
}
```

**Failure Scenarios**:

1. **No active subscription** (404 Not Found):
```json
{
    "error": "No active subscription found"
}
```

2. **User has no organization** (400 Bad Request):
```json
{
    "error": "User has no organization"
}
```

3. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**What User CAN Do**:
- Cancel their organization's subscription
- Receive confirmation email

**What User CANNOT Do**:
- Cancel another organization's subscription
- Cancel without being in an organization
- Cancel without active subscription

**Important Rules**:
- Authentication required
- Multi-tenancy: Can only cancel own organization's subscription
- Sends cancellation email to user
- Updates subscription status to "canceled"

---

## NEW: Step 14: Update Subscription (Upgrade/Downgrade)

### Endpoint: POST /api/subscription/update/

**Purpose**: Upgrade or downgrade the organization's subscription plan.

**Request**:
```http
POST http://localhost:8000/api/subscription/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "plan_id": 3
}
```

**Success Response** (200 OK):
```json
{
    "message": "Subscription updated successfully",
    "new_plan": "Enterprise"
}
```

**Failure Scenarios**:

1. **No active subscription** (404 Not Found):
```json
{
    "error": "No active subscription found"
}
```

2. **Missing plan_id** (400 Bad Request):
```json
{
    "error": "plan_id is required"
}
```

3. **Invalid plan_id** (404 Not Found):
```json
{
    "error": "Invalid plan_id"
}
```

**What User CAN Do**:
- Upgrade to higher-tier plan
- Downgrade to lower-tier plan
- Change billing to different plan

**What User CANNOT Do**:
- Update another organization's subscription
- Skip providing plan_id
- Use non-existent plan

**Important Rules**:
- Authentication required
- Multi-tenancy: Can only update own organization's subscription
- Sends update confirmation email
- Proration is handled by Stripe

---

## NEW: Step 15: Update User Profile

### Endpoint: PATCH /api/user/update/

**Purpose**: Update the authenticated user's profile (email, name).

**Request**:
```http
PATCH http://localhost:8000/api/user/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "email": "newemail@company.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Success Response** (200 OK):
```json
{
    "message": "Profile updated successfully",
    "email": "newemail@company.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Failure Scenarios**:

1. **No authentication** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**What User CAN Do**:
- Update own email address
- Update first name
- Update last name

**What User CANNOT Do**:
- Update another user's profile
- Change username
- Change organization

**Important Rules**:
- Authentication required
- Only email, first_name, last_name can be updated
- Username and organization are immutable via API

---

## NEW: Step 16: Send Subscription Created Email

### Endpoint: POST /api/email/subscription-created/

**Purpose**: Send subscription confirmation email to the user.

**Request**:
```http
POST http://localhost:8000/api/email/subscription-created/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
    "message": "Email sent successfully"
}
```

**Failure Scenarios**:

1. **No subscription found** (404 Not Found):
```json
{
    "error": "No active subscription found"
}
```

**What User CAN Do**:
- Request resend of subscription confirmation email

**What User CANNOT Do**:
- Send emails to other users

**Important Rules**:
- Authentication required
- Sends to authenticated user's email

---

## NEW: Step 17: Send Payment Success Email

### Endpoint: POST /api/email/payment-success/

**Purpose**: Send payment confirmation email to the user.

**Request**:
```http
POST http://localhost:8000/api/email/payment-success/
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
    "message": "Payment confirmation email sent"
}
```

**Failure Scenarios**:

1. **No subscription found** (404 Not Found):
```json
{
    "error": "No subscription found"
}
```

**What User CAN Do**:
- Request resend of payment confirmation email

**What User CANNOT Do**:
- Send payment emails for other organizations

**Important Rules**:
- Authentication required
- Multi-tenancy: Can only send for own organization

---

## NEW: Team Roles Feature

### User Roles

The system supports two roles:

| Role | Description |
|------|-------------|
| **admin** | Can manage organization, view all data, cancel/update subscriptions |
| **member** | Can view data, use the service |

**Default Role**: When a user is created, they are assigned "member" role.

**Setting Role at Registration**:

```http
POST http://localhost:8000/api/user/register/
Content-Type: application/json

{
    "username": "admin_user",
    "email": "admin@techcorp.com",
    "password": "SecurePass123!",
    "organization": 1,
    "role": "admin"
}
```

**What Admins CAN Do**:
- All member actions
- Cancel subscription
- Update subscription plan
- View admin dashboard

**What Members CAN Do**:
- View plans
- Subscribe to plan
- View own organization users
- Download invoice
- Update own profile

**Important Rules**:
- Role is set at user registration
- Currently no API to change role after creation
- Role affects admin dashboard access (planned)

---

## NEW: Rate Limiting

### Configuration

Rate limiting is configured in settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'login': '10/min',
    }
}
```

**Rate Limits**:

| Endpoint Type | Limit |
|---------------|-------|
| General anonymous | 100 requests/day |
| Authenticated user | 1000 requests/day |
| Login endpoints | 10 requests/minute |

**What User CAN Do**:
- Make up to 1000 requests/day as authenticated user
- Make up to 100 requests/day without authentication

**What User CANNOT Do**:
- Exceed rate limits
- Spam login endpoints
- Abuse the API

**Important Rules**:
- Rate limiting prevents abuse
- 429 Response Too Many Requests when exceeded
- Login endpoints have stricter limits

---

## Extended Test Workflow with New Features

```
Step 1:     GET /                          → Verify API is running
Step 2:     POST /api/organization/          → Create Organization + Stripe Customer
Step 3:     POST /api/user/register       → Create Admin User
Step 4:     POST /api/user/register       → Create Member User
Step 5:     POST /api/token/           → Login (Get JWT Token)
Step 6:     POST /api/token/refresh     → Refresh JWT Token
Step 7:     GET /api/plans/           → View Available Plans
Step 8:     POST /api/subscribe/       → Create Stripe Checkout Session
Step 9:     (Manual Payment)         → User completes payment on Stripe
Step 10:    POST /api/stripe/webhook/  → Handle Subscription Events
Step 11:    GET /api/my-users/         → View Organization Users
Step 12:    GET /api/invoice/{id}/    → Download Invoice PDF
Step 13:    GET /api/admin-dashboard/  → View Organization Stats
Step 14:    POST /api/subscription/cancel/     → Cancel Subscription
Step 15:    POST /api/subscription/update/     → Update (Upgrade/Downgrade) Plan
Step 16:    PATCH /api/user/update/      → Update Profile
Step 17:    POST /api/email/subscription-created/ → Send Confirmation Email
Step 18:    POST /api/email/payment-success/   → Send Payment Email
Step 19:    DELETE /api/user/delete/    → Delete (Soft) User
```

---

## Extended Endpoint Matrix

| Method | Endpoint | Auth Required | Admin Only |
|--------|----------|--------------|-------------|
| GET | / | No | No |
| POST | /api/organization/register/ | No | No |
| POST | /api/user/register/ | No | No |
| POST | /api/token/ | No | No |
| POST | /api/token/refresh/ | No | No |
| GET | /api/plans/ | Yes | No |
| POST | /api/subscribe/ | Yes | No |
| POST | /api/stripe/webhook/ | No | No |
| GET | /api/my-users/ | Yes | No |
| GET | /api/invoice/{id}/ | Yes | No |
| GET | /api/admin-dashboard/ | Yes | No |
| POST | /api/subscription/cancel/ | Yes | No |
| POST | /api/subscription/update/ | Yes | No |
| PATCH | /api/user/update/ | Yes | No |
| POST | /api/email/subscription-created/ | Yes | No |
| POST | /api/email/payment-success/ | Yes | No |
| DELETE | /api/user/delete/ | Yes | No |

---

## Postman Extended Test Order

### Admin User Test Flow:

1. **Create Organization**:
```bash
POST {{base_url}}/api/organization/register/
Body: {"name": "TechCorp Inc."}
```

2. **Register Admin User**:
```bash
POST {{base_url}}/api/user/register/
Body: {"username": "admin1", "password": "Pass123!", "organization": {{organization_id}}, "email": "admin@techcorp.com", "role": "admin"}
```

3. **Login**:
```bash
POST {{base_url}}/api/token/
Body: {"username": "admin1", "password": "Pass123!"}
```
→ Save `access` to {{access_token}}

4. **Cancel Subscription** (after having one):
```bash
POST {{base_url}}/api/subscription/cancel/
Headers: Authorization: Bearer {{access_token}}
```

5. **Update Subscription**:
```bash
POST {{base_url}}/api/subscription/update/
Headers: Authorization: Bearer {{access_token}}
Body: {"plan_id": 3}
```

### Member User Test Flow:

1. **Register Member User**:
```bash
POST {{base_url}}/api/user/register/
Body: {"username": "member1", "password": "Pass123!", "organization": {{organization_id}}, "email": "member@techcorp.com", "role": "member"}
```

2. **Login**:
```bash
POST {{base_url}}/api/token/
Body: {"username": "member1", "password": "Pass123!"}
```

3. **Update Profile**:
```bash
PATCH {{base_url}}/api/user/update/
Headers: Authorization: Bearer {{access_token}}
Body: {"first_name": "John", "last_name": "Doe"}
```

4. **Send Subscription Email**:
```bash
POST {{base_url}}/api/email/subscription-created/
Headers: Authorization: Bearer {{access_token}}
```

### Rate Limit Testing:

1. **Test Login Rate Limit** (10/min):
```bash
# Make 11 rapid login attempts
POST {{base_url}}/token/
Body: {"username": "admin1", "password": "wrongpass"}
# 11th attempt should return 429
```

2. **Test General Rate Limit**:
```bash
# Make 101 rapid authenticated requests
GET {{base_url}}/api/plans/
Headers: Authorization: Bearer {{access_token}}
# 101st request should return 429
```

---

## NEW: Step 19: Delete User (Soft Delete)

### Endpoint: DELETE /api/user/delete/

**Purpose**: Soft delete a user (sets is_active=False). Only admins can delete other users.

**Request**:
```http
DELETE http://localhost:8000/api/user/delete/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "user_id": 2
}
```

**Success Response** (200 OK):
```json
{
    "message": "User deleted successfully",
    "user_id": 2
}
```

**Failure Scenarios**:

1. **User not found** (404 Not Found):
```json
{
    "error": "User not found"
}
```

2. **Missing user_id** (400 Bad Request):
```json
{
    "error": "user_id is required"
}
```

3. **Cannot delete from other organization** (403 Forbidden):
```json
{
    "error": "Cannot delete users from other organization"
}
```

4. **Member trying to delete another user** (403 Forbidden):
```json
{
    "error": "Only admins can delete other users"
}
```

**What Admins CAN Do**:
- Delete any user in their organization
- Soft delete (user is set to inactive)

**What Members CAN Do**:
- Soft delete their own account

**What Users CANNOT Do**:
- Delete users from other organizations
- Hard delete (permanent removal)
- Reactivate deleted users via this endpoint

**Important Rules**:
- Authentication required
- Multi-tenancy: Cannot delete from other orgs
- Role check: Only admins can delete others
- Soft delete preserves data integrity

**Test Data**:
- Valid user_id: Existing user ID in organization
- Invalid user_id: 999, 0

---

## Role-Based Access Control Summary

| Action | Admin | Member |
|--------|-------|--------|
| View plans | yes | yes |
| Subscribe to plan | yes | yes |
| Cancel subscription | yes | No |
| Update subscription | yes | No |
| View all users | yes | yes |
| Download invoice | yes | yes |
| View admin dashboard | yes | yes |
| Update profile | yes | yes |
| Delete user (self) | yes | yes |
| Delete user (others) | yes | No |
| Update profile | yes | yes |
| Send confirmation email | yes | yes |

## Ended Broo HEHE