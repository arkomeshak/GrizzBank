from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("transfer", transfer, name="transfer"),
    path("login", login, name="login"),
    path("create", create_account, name="create_account"),
    path("withdrawDeposit", withdraw_deposit, name="withdraw_deposit"),
    path("resetPassword", reset_password, name="reset_password")
]
