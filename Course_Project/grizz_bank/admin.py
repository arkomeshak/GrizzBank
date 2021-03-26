from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Client)
admin.site.register(Username)
admin.site.register(Email)
admin.site.register(PhoneNumber)
admin.site.register(Account)
admin.site.register(InterestRate)
admin.site.register(RequestReset)

