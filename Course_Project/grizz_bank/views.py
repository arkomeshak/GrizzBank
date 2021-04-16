import random
import hashlib
from django.core.mail import *
from django.conf import settings

from django.shortcuts import render, redirect
from .models import *  # import all of the model classes
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction, IntegrityError
from django.contrib import messages

import re  # regular expressions
import decimal
import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User

SESSION_EXPIRATION = 60  # login cookie time to live in minutes

# Create your views here.


def index(request):
    """
    def create_account_data_list(accounts):
        # dictionary mapping account type key to an actual account type name
        types = {"S": "Savings", "C": "Checking"}
        # List comprehension returning a list of dicitonaries containing account type, balance, and ID
        acct_data = [{"type": types[acct.acct_type], "bal": acct.acct_bal, "id": acct.acct_id} for acct in accounts]
        return acct_data
    """
    if "sessionid" not in request.COOKIES or (request.session.get_expiry_age() == 0):
        print("Session not set, or expired")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=expired_session")
    uname = request.session.get("uname", None)
    if request.session.get("uname", None) is None:
        print("uname is None :)")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=invalid_session")

    # TODO: Add login cookie check/refresh here, on failure redirect to login page
    print(f"Cookies: {request.COOKIES}")
    context = {}
    uname =  request.session.get("uname", None)
    print(request.session.get_expiry_age())
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

    #this view renders the create_account template,
    #redirects the page to the index or home page,
    # and should send a message request to display a
    # Success! message if account creation is successful
def create_account(request):
    context = {}
    #call create_client view
    #create_client(request)
    #return redirect('index')
    return render(request, "grizz_bank/create_account.html", context)
    messages.info(request, 'Your account has been created successfully!')

def reset_password(request):
    if "sessionid" not in request.COOKIES or (request.session.get_expiry_age() == 0):
        print("Session not set, or expired")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=expired_session")
    if request.session.get("uname", None) is None:
        print("uname is None :)")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=invalid_session")
    context ={}
    return render(request, "grizz_bank/reset_password.html", context)


def login(request):
    """

    :param request:
    :return:
    """
    '''
    print("cookies:", request.COOKIES)
    print(request.COOKIES.get('expiration'))
    print(date)
    print(date < request.COOKIES.get('expiration'))
    '''
    date = str(datetime.datetime.now())
    if "expiration" in request.COOKIES and date < request.COOKIES.get('expiration'):
        return HttpResponseRedirect(f"/grizz_bank?uname={request.COOKIES.get('uname')}&status=Login_success")
    else:
        context ={}
        return render(request, "grizz_bank/login.html", context)


def transfer(request):
    """
    Django view handling business logic to render a web page where users transfer money between their checkings and
    savings accounts.
    :param request: Django HTTPS GET Request
    :return: HTTPS Response with HTML rendered per transfer.html template
    """
    # Redirect to login if client not logged in
    if "sessionid" not in request.COOKIES or (request.session.get_expiry_age() == 0):
        print("Session not set, or expired")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=expired_session")
    uname = request.session.get("uname", None)
    if request.session.get("uname", None) is None:
        print("uname is None :)")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=invalid_session")
    context = fetch_acct_data(uname)
    return render(request, "grizz_bank/transfer.html", context)


def deposit(request):
    """
    Django view to handle business logic needed to render the deposit page a client uses to deposit money into one of
    their checking or savings accounts.
    :param request: HTTP django request object
    :return: Django HTTPResponse with rendered deposit page HTML
    """
    # Redirect to login if client not logged in or session expired
    if "sessionid" not in request.COOKIES or (request.session.get_expiry_age() == 0):
        print("Session not set, or expired")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=expired_session")
    uname = request.session.get("uname", None)
    if request.session.get("uname", None) is None:
        print("uname is None :)")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=invalid_session")
    context = fetch_acct_data(uname)
    return render(request, "grizz_bank/deposit.html", context)


def delete(request):
    """
    Django view which renders the delete account template.
    :param request: Djanto HTTP GET request
    :return: rendered HTTP response for the delete index
    """
    if "sessionid" not in request.COOKIES or (request.session.get_expiry_age() == 0):
        print("Session not set, or expired")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=expired_session")
    uname = request.session.get("uname", None)
    if request.session.get("uname", None) is None:
        print("uname is None :)")
        return HttpResponseRedirect(f"/grizz_bank/login/?status_message=invalid_session")
    context = fetch_acct_data(uname)
    # Check if use failed to select the confirm deletion checkbox
    if "err_msg" in request.GET:
        if request.GET["err_msg"] == "confirm_delete":
            context["err_msg"] = "Please Check the box confirming deletion of your account."
        elif request.GET["err_msg"] == "bad_acct_selection":
            context["err_msg"] = """Please select a single account to delete, and a single account to place 
                                    remaining balance into."""
    return render(request, "grizz_bank/delete.html", context)

# ===================== Business Logic Views =====================
@transaction.atomic
def create_client(request):
    #creation of salt and hash of password
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars = []
    for i in range(10):
        chars.append(random.choice(alphabet))
    salt = "".join(chars)
    password = request.POST["password"]
    user = request.POST["username"]
    phone = request.POST["phonenumber"]
    emailGiven = request.POST["email"]
    sav_bal = decimal.Decimal(float(request.POST["initialsavingsbalance"]))

    #populate tables: Client, Username_archive, Email_archive, Phone_number_archive
    with transaction.atomic():
        client = Client(f_name = request.POST["firstname"],
                        l_name = request.POST["lastname"],
                        pword_salt = salt,
                        pword_hash = hashlib.sha256(str(password+salt).encode('utf-8')).hexdigest(),
                        email = emailGiven,
                        username = user,
                        phone_number = phone)

    client.save()

    userArchive = UsernameArchive(username = user,
                                  client = client)

    phoneNumberArchive = PhoneNumberArchive(client = client,
                                            phone_number = phone)

    emailArchive = EmailArchive(client = client,
                                email = emailGiven)

    #save all of the data in the tables
    userArchive.save()
    phoneNumberArchive.save()
    emailArchive.save()
    request.session["id"] = client.pk
    new_response = HttpResponse(request)

    #create checking and savings accounts
    chk_account = Account(acct_bal = decimal.Decimal(0),
                          acct_type="C",
                          client=client)
    chk_account.save()

    sav_account = Account(acct_bal = sav_bal,
                          acct_type = "S",
                          client=client)
    sav_account.save()
    return HttpResponseRedirect("/grizz_bank/")

def set_password(request):
    pass

def reset_password_handler(request):
    context = {}
    print(request.session.get("uname", None))
    query = Client.objects.get(username= request.session.get("uname", None))
    uname = query.username
   
    try:
        if request.method == 'POST':
            print(request.POST)
            print("past IF POST")
            form = AuthenticationForm(request, data=request.POST)
            print(request.POST)
            print(form.is_valid())
            print(form.errors)
            if not form.is_valid():
                #The password from the user
                passwordCurrent = request.POST.get('password')
                print(passwordCurrent)
                #the salt from the database
                salt = query.pword_salt
                print(salt)
                saltedAndHashedGuess = salt + passwordCurrent  #hash(salt + passwordGuess)
                print("pword plus salt", saltedAndHashedGuess)
                #the salted and hashed password from the database
                correctPwHash = (query.pword_salt) + (query.pword_hash)
                print("correct:", correctPwHash)
                if (saltedAndHashedGuess == correctPwHash):
                    passwordNew = request.POST.get('New_password')
                    passwordConfirm = request.POST.get('confirm_password')
                    if (passwordNew == passwordConfirm):
                        with transaction.atomic():
                            pwordChange = Client.objects.get(username=uname)
                            pwordChange.pword_hash = passwordConfirm
                            pwordChange.save()
                        response = HttpResponseRedirect(f"/grizz_bank/?uname={uname}&status=Reset_success")
                        return response
                    else:
                        messages.error(request, 'make sure the new password field matched the confirm new password field')
                        return HttpResponseRedirect(f"/grizz_bank/reset_password/?uname={uname}&status=New_Password_Didnt_Match")
                else:
                    messages.error(request, 'incorrect password')
                    return HttpResponseRedirect(f"/grizz_bank/reset_password/?uname={uname}&status=Reset_Failed")
    except Client.DoesNotExist:
        raise RuntimeError("Account not found")
    return render(request, "grizz_bank/index.html", context)

def login_handler(request):
    try:
        usernameGuess = request.POST.get('username')
        query = Client.objects.get(username=usernameGuess)
        print(usernameGuess)
        uname = query.username
        print(query.pword_salt)
  
        if request.method == 'POST':
            print(request.POST)
            print("past IF POST")
            form = AuthenticationForm(request, data=request.POST)
            print(request.POST)
            print(form.is_valid())
            print(form.errors)
            if not form.is_valid():
                #The password from the user
                passwordGuess =request.POST.get('password')
                print(passwordGuess)
                #the salt from the database
                salt = query.pword_salt
                print(salt)
                saltedAndHashedGuess = salt + passwordGuess   #hash(salt + passwordGuess)
                print("pword plus salt", saltedAndHashedGuess)
                #the salted and hashed password from the database
                correctPwHash = (query.pword_salt) + (query.pword_hash)
                print("correct:", correctPwHash)
                if (saltedAndHashedGuess == correctPwHash):
                    #login success
                    # Set the uname session value to username the user logged in with
                    if (request.POST.get('remember') == 'on'):
                        print(request.POST.get('remember'))
                        
                        request.session["uname"] = uname
                        request.session.set_expiry(SESSION_EXPIRATION * 60)  # expires in SESSION_EXPIRATION * 60s seconds (Final Suggestion: if remember me is checked we can set session to last mabye 7 days)
                    
                    else:
                        print(request.POST.get('remember'))
                        request.session["uname"] = uname
                        request.session.set_expiry(SESSION_EXPIRATION * 30)  # expires in SESSION_EXPIRATION * 30s seconds (Final Suggestion: if remember me is unchecked we can set session to last 1 day)
                    response = HttpResponseRedirect(f"/grizz_bank/?uname={uname}&status=Login_success")
                    return response
                else:
                    messages.error(request, 'username or password not correct')
                    return HttpResponseRedirect(f"/grizz_bank/login?&status=Login_Failed")
    except Client.DoesNotExist:
        return HttpResponseRedirect(f"/grizz_bank/login?&status=Account_Not_Found")


def logout_handler(request):
    """
    Simple handler which logs the user out, flushing the session from the DB and removing the session cookie.
    Redirects to login page.
    :param request: Django request
    :return: HttpRedirectResponse
    """
    if "sessionid" in request.COOKIES:
        request.session.flush()
        return HttpResponseRedirect("../grizz_bank/login/?status_message=logged_out")
    # Client wasn't logged in the first place (session likely already expired)
    return HttpResponseRedirect("../grizz_bank/login/")


@transaction.atomic
def transfer_handler(request):
    """
    Handles incoming POST request sent from the transfer page requesting funds
    :param request: POST request with account ids to transfer to, and from, as well as quantities
    :return: HTTP response, or redirect
    """

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
        if not (len(amount) > 0 or amount.replace(".", "").isnumeric()):
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
        return HttpResponseRedirect(f"/grizz_bank?uname={uname}&status=transfer_success")

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

@transaction.atomic
def deposit_handler(request):
    """
    Handles incoming POST Requests sent fromt transfer page to
    :param request: HTTP POST request with
    :return: HTTP Redirect
    """
    #return HttpResponseRedirect(f"/grizz_bank/?uname={request.POST['uname']}&amt={request.POST['deposit_amount']}")
    try:
        for key in ["uname", "deposit_amount"]:
            if key not in request.POST:
                raise KeyError(f"Deposit handler error: POST request missing {key} value")
        if "check_img" not in request.FILES:
            raise KeyError(f"Deposit handler error: POST request missing the check image")
        uname, check_img, amount = request.POST["uname"], request.FILES["check_img"], request.POST["deposit_amount"]
        # In lieu of a computer vision call to verify check is valid and matches amount specified, reject if
        # "invalid" is part of the filename
        if "invalid" in check_img.name.lower():
            raise ValueError(f"Deposit handler error: Invalid check submitted")
        elif not amount.replace(".", "").isnumeric():
            raise ValueError(f"Deposit handler error: Invalid deposit amount {amount}")
        amount = decimal.Decimal(float(amount))
        # Get the account id
        id = get_acct_id(request.POST.keys())
        if id == -1:
            raise KeyError(f"Deposit handler error: No account selected as deposit destination")
        # Perform the transfer as an ACID transaction
        with transaction.atomic():
            dest_acct = Account.objects.get(pk=id)
            dest_acct.acct_bal += amount
            dest_acct.save()
            # transfer successfully occurred
        return HttpResponseRedirect(f"/grizz_bank/?uname={request.POST['uname']}&status_msg=deposit_success")
    except KeyError as e:
        print(e)
        print(f"Post data: {request.POST}")
        return HttpResponseRedirect(f"/grizz_bank/deposit/?uname={request.POST['uname']}&error_msg=invalid_input_error")
    except ValueError as e:
        print(e)
        print(f"Post data: {request.POST}")
        return HttpResponseRedirect(f"/grizz_bank/deposit/?uname={request.POST['uname']}&error_msg=bad_value_error")
    except IntegrityError as e:
        print(e)
        print(f"POST data: {request.post}")
        return HttpResponseRedirect(f"/grizz_bank/deposit/?uname={uname}&error_msg=deposit_transaction_error")
    except Exception as e:
        print(e)
        print(f"Post data: {request.POST}")
        return HttpResponseRedirect(f"/grizz_bank/deposit/?uname={request.POST['uname']}&error_msg=unknown_error")


def withdraw_handler(request):
    pass


    #populate tables:Account and Interest Rate
def create_savings(request):
    sav_account = Account(acct_bal= decimal.Decimal(float(request.POST["initialsavingsbalance"])),
                          acct_type="S",
                          client=client)

    sav_account.save()

    #populate tables: Account and Interest Rate
def create_checking(request):
    chk_account = Account(acct_bal=0,
                          acct_type="C",
                          client=client)

    chk_account.save()

@transaction.atomic
def delete_handler(request):
    """
    Django view which handles business logic for the deletion of a bank account,
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            print("post:", request.POST)
            uname = request.session.get("uname")
            from_id, to_id = get_account_ids(request.POST)
            # Can't deposit into same acct your are deleting
            if from_id == to_id: return HttpResponseRedirect("./err_msg=bad_acct_Selection")
            if "confirm_delete" not in request.POST or request.POST["confirm_delete"][0] != "on":
                raise ValueError("User didn't confirm acct deletion")
            client_id = Client.objects.get(username=uname).client_id
            to_delete = Account.objects.get(pk=from_id)
            transfer_to = Account.objects.get(pk=to_id)
            if client_id == to_delete.client.pk == transfer_to.client.pk:
                # all good to perform the delete transaction
                with transaction.atomic():
                    remaining_bal = to_delete.acct_bal
                    transfer_to.acct_bal += remaining_bal
                    to_delete.delete()
                    transfer_to.save()
            else:
                msg = "Somehow account to delete and account to deposit to did not have same key as client " + \
                        f"\n\tclient id:{client_id}" + f" delete id: {to_delete.pk}" + f" dest id: {from_id}"
                raise Exception(msg)
            return HttpResponseRedirect("../grizz_bank/?status_msg=successful_deletion")
        except ValueError as e:
            print(e)
            return HttpResponseRedirect("./delete/?err_msg=confirm_delete")
        except RuntimeError as e:
            print(e)
            return  HttpResponseRedirect("./?err_msg=bad_acct_selection")
        except Exception as e:
            print(e)
            return HttpResponseRedirect("../grizz_bank/?err_msg=unkown_delete_err")
    else:
        print(f"Attempted acces sof delete_handler via invalid thing")
        return HttpResponseRedirect("../grizz_bank/")



# View Helper Functions for use in multiple views

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


def fetch_acct_data(uname):
    """
    Helper function which retrieves savings/checking accounts, from the database, and stores them in a
    dicitonary which can be used as a django context for template rendering. Used by various vierws rendering
    templates w/ account balances.
    :param uname: string
    :return: python dictionary
    """
    acct_data = {}
    try:
        client_id = Client.objects.get(username=uname).client_id
        client_accounts = Account.objects.filter(client_id=client_id)
        # List comprehension to build a list of python dictionaries containing account data into the context
        acct_data["account_data"] = create_account_data_list(client_accounts)
        acct_data["uname"] = uname
        acct_data["error"] = False
    except Exception as e:
        # If an error happens log to console, set context error flag true, and make account data an empty list
        print(e)
        acct_data["error"] = True
        acct_data["account_data"] = list()

    return acct_data


def get_acct_id(post_keys):
    """
    Helper function which takes in an iterable of keys in a POST request, and returns the account key of the
    savings or checking account within the keys if one exists. Return -1 if no account found
    :param post_keys: iterable of key values from a POST request dictionary
    :return: account id as an integer, -1 if DNE
    """
    for k in post_keys:
        print(f"type of key: {type(k)}")
        res = re.match("(del)|(to)|(from)_acct", k)
        if res is not None:
            return int(k.split("acct")[1])
    return -1


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


def logout(http_request, status_message=None):
    """
    Implement a logout routine which deletes a user's session, and their
    sessionid in their cookies. Returns an HttpResponseRedirect to login page.
    :param http_request: Django Request object
    :param status_message: string to be made as a status message in GET request
    :return: HttpResponseRedirect
    """
    if "sesisonid" in http_request.COOKIES:
        http_request.session.flush()
    if status_message is None:
        return HttpResponseRedirect("grizz_bank/login/")
    return HttpResponseRedirect(f"grizz_bank/login/?status_message={status_message}")
