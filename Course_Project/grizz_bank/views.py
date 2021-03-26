from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    context = {}
    return render(request, "grizz_bank/index.html", context)


def create_account(request):
    pass


def reset_password(request):
    pass


def login(request):
    pass


def transfer(request):
    pass


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
