from .models import *

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Custom ModelView for each model to include foreign key relationships


class UserAdmin(ModelView):
    can_create = False
    column_list = ['id', 'name', 'username', 'email',
                   'phone', 'role', 'status']  # Show relevant columns
    form_columns = ['name', 'password', 'username', 'email',
                    'phone', 'role', 'address', 'status']  # Fields in the form


class ProfessionalsAdmin(ModelView):
    can_create = False
    column_list = ['id', 'business_name', 'YoE', 'address',
                   'pin', 'status', 'user']  # Show foreign key 'user'
    form_columns = ['business_name', 'YoE', 'address', 'pin',
                    'status', 'user']  # Dropdown for selecting a user


class OrderAdmin(ModelView):
    can_create = False
    column_list = ['order_id', 'user', 'professional', 'status',
                   'rating']  # Show foreign keys 'user' and 'professional'
    # Dropdowns for 'user' and 'professional'
    form_columns = ['user', 'professional', 'status', 'rating']


class ServicesAdmin(ModelView):
    can_create = False
    column_list = ['id', 'service', 'description', 'price',
                   'professional']  # Show foreign key 'professional'
    # Dropdown for selecting a professional
    form_columns = ['service', 'description', 'price', 'professional']
