from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("transfer/", transfer, name="transfer"),
    path("login/", login, name="login"),
    path("create/", create_account, name="create_account"),
    path("withdraw_deposit/", withdraw_deposit, name="withdraw_deposit"),
    path("reset_password/", reset_password, name="reset_password")
]
