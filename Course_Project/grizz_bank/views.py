from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    context = {}
    return render(request, "grizz_bank/index.html", context)


def create_account(request):
    context = {}
    return render(request, "grizz_bank/create_account.html", context)


def reset_password(request):
    pass


def login(request):
    pass
    context ={}

    return render(request, "grizz_bank/login.html", context)


def transfer(request):
    """
    Django view handling business logic to render a web page where users transfer money between their checkings and
    savings accounts.
    :param request: Django HTTPS GET Request
    :return: HTTPS Response with HTML rendered per transfer.html template
    """
    context ={}

    return render(request, "grizz_bank/transfer.html", context)


def withdraw_deposit(request):
    pass

# ===================== Business Logic Views =====================


def create_client(request):
    pass


def set_password(request):
    pass


def login_handler(request):
    pass


def transfer_handler(request):
    pass


def deposit_handler(request):
    pass


def withdraw_handler(request):
    pass


def create_savings(request):
    pass


def create_checking(request):
    pass
