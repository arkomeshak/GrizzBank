from django.db import models
from django.utils.datetime_safe import datetime
import decimal
from datetime import datetime, timedelta

# Create your models here.


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    f_name = models.CharField(max_length=45, null=False, blank=False, default="")
    l_name = models.CharField(max_length=45, null=False, blank=False, default="")
    pword_salt = models.CharField(max_length=10, null=True)
    pword_hash = models.CharField(max_length=300, null=True)
    email = models.CharField(max_length=50, null=False, blank=False, default="", unique=True)
    username = models.CharField(max_length=45, null=False, blank=False, default="", unique=True)
    phone_number = models.CharField(max_length=10, null=False, blank=False, default="", unique=True)


class UsernameArchive(models.Model):
    archive_uname_id = models.AutoField(primary_key=True)
    username = models.fields.CharField(max_length=45)
    creation_date = models.DateTimeField(null=False, default=datetime.now)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class PhoneNumberArchive(models.Model):
    archive_phone_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    phone_number = models.fields.CharField(max_length=10)
    creation_date = models.DateTimeField(null=False, default=datetime.now)


class InterestRate(models.Model):
    acct_type = models.fields.CharField(max_length=1, primary_key=True)
    interest_rate = models.fields.DecimalField(max_digits=3, decimal_places=2, default=0.0)


class EmailArchive(models.Model):
    archive_email_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    email = models.fields.CharField(max_length=50)
    creation_date = models.DateTimeField(null=False, default=datetime.now)


class Account(models.Model):
    acct_id = models.fields.AutoField(primary_key=True)
    acct_bal = models.fields.DecimalField(max_digits=8, decimal_places=2, null=False)
    acct_type = models.fields.CharField(max_length=1)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class RequestReset(models.Model):
    reset_id = models.fields.AutoField(primary_key=True)
    verification_string = models.fields.CharField(max_length=45, null=False, unique=True)
    expires = models.fields.DateTimeField(editable=False, null=False, default=(datetime.now() + timedelta(minutes=10)))
