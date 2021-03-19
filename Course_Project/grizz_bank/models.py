from django.db import models
from django.utils.datetime_safe import datetime
import decimal
from datetime import datetime, timedelta

# Create your models here.


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    f_name = models.CharField(max_length=45, null=False)
    l_name = models.CharField(max_length=45, null=False)
    pword_salt = models.CharField(max_length=10, null=True)
    pword_hash = models.CharField(max_length=300, null=True)


class Username(models.Model):
    username = models.fields.CharField(max_length=45)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, primary_key=True)


class PhoneNumber(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.fields.CharField(max_length=10)


class InterestRate(models.Model):
    acct_type = models.fields.CharField(max_length=1, primary_key=True)
    interest_rate = models.fields.DecimalField(max_digits=3, decimal_places=2, default=0.0)


class Email(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, primary_key=True)
    email = models.fields.CharField(max_length=50)


class Account(models.Model):
    acct_id = models.fields.AutoField(primary_key=True)
    acct_bal = models.fields.DecimalField(max_digits=8, decimal_places=2, null=False)
    acct_type = models.fields.CharField(max_length=1)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class RequestReset(models.Model):
    reset_id = models.fields.AutoField(primary_key=True)
    verification_string = models.fields.CharField(max_length=45, null=False)
    expires = models.fields.DateTimeField(editable=False, null=False, default=(datetime.now() + timedelta(minutes=10)))
