# -*- coding: UTF-8 -*-
import re
import smtplib
from validate_email import validate_email

def is_mail(val):
    val = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', val)
    return (val is not None)

def is_valid(val):
    return (validate_email(val) == True)

def is_verify(val):
    return (validate_email(val, verify=True) == True)

def is_valid_mx(val):
    return (validate_email(val, check_mx=True) == True)
