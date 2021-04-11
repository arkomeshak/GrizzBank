import random
import hashlib

from django.shortcuts import render
from .models import *  # import all of the model classes
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction, IntegrityError
from django.contrib import messages

import re  # regular expressions
import decimal

# Create your views here.


def index(request):
    def create_account_data_list(accounts):
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

    
    return render(request, "grizz_bank/index.html", context)


def create_account(request):
    context = {}
    return render(request, "grizz_bank/create_account.html", context)
    messages.info(request, 'Your account has been created successfully!')
    #return HttpResponseRedirect('/grizz_bank/')
    #do i have a redirect or a render???
    #where do i put this redirect

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
        # List comprehension returning a list of dictionaries containing account type, balance, and ID
        acct_data = [{"type": types[acct.acct_type], "bal": acct.acct_bal, "id": acct.acct_id} for acct in accounts]
        return acct_data

    context = {}
    uname = request.GET["uname"]
    try:
        client_id = Client.objects.get(username=uname).client_id
        client_accounts = Account.objects.filter(client_id=client_id)
        # List comprehension to build a list of python dictionaries containing account data into the context
        context["account_data"] = create_account_data_list(client_accounts)
        context["uname"] = uname
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
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(10):
        chars.append(random.choice(alphabet))
    salt = "".join(chars)
    password = request.POST("password")
    user = request.POST("username")

    client = Client(f_name = request.POST("firstname"),
                    l_name = request.POST("lastname"),
                    pword_salt = password+salt,
                    pword_hash = hashlib.sha256(password+salt),
                    email = request.POST("email"),
                    username = user,
                    phone_number = request.POST("phonenumber"))
    client.save()
    #no idea if this redirect is right...I'm tired lol
    #return HttpResponseRedirect('/grizz_bank/?uname='+user)


def set_password(request):
    pass


def login_handler(request):
    pass


@transaction.atomic
def transfer_handler(request):
    """
    Handles incoming POST request sent from the transfer page requesting funds
    :param request: POST request with account ids to transfer to, and from, as well as quantities
    :return: HTTP response, or redirect
    """
    def get_account_ids(post_dict):
        """
        Helper function extracting the acount ids from the POST request's keys
        :param post_dict: python dictionary
        :return: (int: from_id, int: to_id)
        """
        from_id, to_id = None, None
        for key in post_dict.keys():
            from_match = re.match("from_acct\d*", key)
            to_match = re.match("to_acct\d*", key)
            # matches can have the id extracted by splitting string on "acct" substring and selecting second half
            if from_match is not None:
                from_id = int(from_match.string.split("acct")[1])
                continue
            if to_match is not None:
                to_id = int(to_match.string.split("acct")[1])
        if (from_id is None) or (to_id is None):
            raise RuntimeError("transfer handler error: no valid to/from account IDs found")
        return from_id, to_id

    uname = ""  # initially set uname to empty string
    try:
        # Check that expected the request was via POST, and correct fields are in the request
        if request.method != "POST":
            raise RuntimeError("Transfer handler expects a post")
        post = request.POST
        for field in ["transfer_amount", "uname"]:
            if field not in post:
                raise RuntimeError(f"Transfer Handler expected the missing field {field} to be in the request.")
        # Retrieve account data from db using data sent by post
        amount, uname = post["transfer_amount"], post["uname"]
        if not (len(amount) > 0 or amount.isnumeric()):
            raise RuntimeError(f"Transfer handler error: Invalid amount passed by user. amount={amount}")
        # Convert ammount to a decimal type from the string
        amount = decimal.Decimal(float(amount))
        from_id, to_id = get_account_ids(post)
        print(f"amount: {amount}")
        if amount <= 0.0:
            raise RuntimeError(f"transfer handler error: invalid transfer amount. Cannot transfer amount <= 0. amount {amount}")
        from_acct = Account.objects.get(pk=from_id)
        # Check that the account transfering from has enough funds
        from_bal = from_acct.acct_bal
        if from_bal < amount:
            errmsg = f"Transfer Handler error: acct# {from_id} has insufficient funds: {from_acct.acct_bal:.2f} needed {amount:.2f}"
            raise RuntimeError(errmsg)
        to_acct = Account.objects.get(pk=to_id)
        # Check that accounts belong to same user
        acct_id = Client.objects.get(username=uname).client_id
        if to_acct.client.pk != from_acct.client.pk or to_acct.client.pk != acct_id or from_acct.client.pk != acct_id:
            print(f"acct_id: {acct_id} from_client_id: {from_acct.client.pk} to_client_id: {to_acct.client.pk}")
            raise RuntimeError(f"Transfer Handler error: account owner mismatch: from owner ID: {from_acct.client} to owner id:{to_acct.client}")
        # Perform the transfer as an ACID transaction
        with transaction.atomic():
            from_acct.acct_bal -= amount
            to_acct.acct_bal += amount
            from_acct.save()
            to_acct.save()
        # transfer successfully occurred
        return HttpResponseRedirect(f"/grizz_bank?uname={uname}?status=transfer_success")

    except IntegrityError as e:
        print(e)
        print(f"POST data: {post}")
        return HttpResponseRedirect(f"/grizz_bank/transfer/?uname={uname}&error_msg=transfer_transaction_error")
    except RuntimeError as e:
        print(e)
        print(f"POST data: {post}")
        return HttpResponseRedirect(f"/grizz_bank/transfer/?uname={uname}&error_msg=transfer_invalid_transfer_error")
    except Exception as e:
        print(e)
        print(f"Post data: {post}")
        return HttpResponseRedirect(f"/grizz_bank/transfer/?uname={uname}&error_msg=unknown_transfer_error")



def deposit_handler(request):
    pass


def withdraw_handler(request):
    pass


def create_savings(request):
    pass


def create_checking(request):
    pass
