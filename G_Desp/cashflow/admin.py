from django.contrib import admin

# Register your models here.
from .models import Category, Inflow, Outflow

admin.site.register(Category)
admin.site.register(Inflow)
admin.site.register(Outflow)
