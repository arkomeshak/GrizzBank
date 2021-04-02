from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Client)
admin.site.register(UsernameArchive)
admin.site.register(EmailArchive)
admin.site.register(PhoneNumberArchive)
admin.site.register(Account)
admin.site.register(InterestRate)
admin.site.register(RequestReset)

