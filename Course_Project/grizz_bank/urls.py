from django.urls import path
from .views import *

urlpatterns = [
    # URLs rendering templates for user visible web pages
    path("", index, name="index"),
    path("transfer/", transfer, name="transfer"),
    path("login/", login, name="login"),
    path("create_account/", create_account, name="create_account"),
    path("withdraw_deposit/", withdraw_deposit, name="withdraw_deposit"),
    path("reset_password/", reset_password, name="reset_password"),
    # Handler URLS
    path("transfer_handler/", transfer_handler, name="transfer_handler"),
    path("deposit_handler/", deposit_handler, name="deposit_handler"),
    path("withdraw_handler/", withdraw_handler, name="withdraw_handler"),
    path("create_savings_handler/", create_savings, name="create_savings_handler"),
    path("create_checking_handler/", create_checking, name="create_checking_handler"),
    path("create_client/", create_client, name="create_client"),
    path("set_password/", set_password, name="set_password")
]
