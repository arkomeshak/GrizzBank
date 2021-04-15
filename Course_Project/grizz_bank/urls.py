from django.urls import path
from .views import *

urlpatterns = [
    # URLs rendering templates for user visible web pages
    path("", index, name="index"),
    path("transfer/", transfer, name="transfer"),
    path("login/", login, name="login"),
    path("create_account/", create_account, name="create_account"),
    path("deposit/", deposit, name="withdraw_deposit"),
    path("reset_password/", reset_password, name="reset_password"),
    path("delete/", delete, name="delete"),
    # Handler URLS
    path("transfer_handler/", transfer_handler, name="transfer_handler"),
    path("login_handler/", login_handler, name="login_Handler"),
    path("deposit_handler/", deposit_handler, name="deposit_handler"),
    path("withdraw_handler/", withdraw_handler, name="withdraw_handler"),
    path("create_savings_handler/", create_savings, name="create_savings_handler"),
    path("create_checking_handler/", create_checking, name="create_checking_handler"),
    path("create_client/", create_client, name="create_client"),
    path("set_password/", set_password, name="set_password"),
    path("reset_password_handler/", reset_password_handler, name="reset_password_handler"),
    path("delete_nahdler", delete_handler, name="delete_handler"),
    path("logout_handler", logout_handler, name="logout_handler")
]
