from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BUA
from .models import *

# Register your models here.

class UserAdmin(BUA):
    fieldsets = BUA.fieldsets+ (
        (                      
            'Type', # you can also use None 
            {
                'fields': (
                    'type',
                ),
            },
        ),
    )

admin.site.register(User,UserAdmin)