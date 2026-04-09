from django.contrib import admin
from .models import Plan, Organization, User, Subscription

admin.site.register(Plan)
admin.site.register(Organization)
admin.site.register(User)
admin.site.register(Subscription)