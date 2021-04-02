from django.shortcuts import render
from .models import *  # import all of the model classes
from django.http import HttpResponse

# Create your views here.


def index(request):
    context = {}
    return render(request, "grizz_bank/index.html", context)


def create_account(request):
    context = {}
    return render(request, "grizz_bank/create_account.html", context)


def reset_password(request):
    context = {}
    return render(request, "grizz_bank/reset_password.html", context)


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
    def create_account_data_list(accounts):
        """
        Helper function which transforms data from a Django Account row object into a list of python dictionaries
        containing account data (type, balance, id)
        rendering in the template.
        :param accounts: list of Account row objects
        :return: python dictionary
        """
        # dictionary mapping account type key to an actual account type name
        types = {"S": "Savings", "C": "Checking"}
        # List comprehension returning a list of dicitonaries containing account type, balance, and ID
        acct_data = [{"type": types[acct.acct_type], "bal": acct.acct_bal, "id": acct.acct_id} for acct in accounts]
        return acct_data

    context = {}
    uname = request.GET["uname"]
    try:
        client_id = Client.objects.get(username=uname).client_id
        client_accounts = Account.objects.filter(client_id=client_id)
        # List comprehension to build a list of python dictionaries containing account data into the context
        context["account_data"] = create_account_data_list(client_accounts)
        context["error"] = False
    except Exception as e:
        # If an error happens log to console, set context error flag true, and make account data an empty list
        print(e)
        context["error"] = True
        context["account_data"] = list()

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
