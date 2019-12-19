
# -*- coding: UTF-8 -*-
import os
import json
import base64
import re
import datetime
import shutil
import random, string

def is_none(obj):
    if obj is None:
        return True
    return False

def is_empty(val):
    return (val is None or len(val) <= 0)

def is_mail(val):
    val = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', val)
    return (val is not None)

def is_exist(obj, key):
    try:
        return key in obj.keys()
    except Exception as e:
        print(str(e))
        return False

def is_json(obj):
    try:
        keys = obj.keys()
        if keys is None:
            data = json.load(obj)
            keys = data.keys()
    except Exception as ex:
        print(str(ex))
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', str(e))
    return (keys is not None and len(keys) > 0)

def is_type(obj, istype):
    if obj is None:
        return None
    # print(str(type(obj)))
    objstr = str(type(obj)).replace("<class '", "").replace("'>", "")
    return (objstr == istype)

class Obj():
    STR = 'str'
    INT = 'int'
    LIST = 'list'
    BOOL = 'bool'
    METHOD = 'method'
    FILESTORAGE = 'werkzeug.datastructures.FileStorage'
    QUEUEPOOL = 'sqlalchemy.pool.impl.QueuePool'

def convert_file_to_b64_string(fullpath):
    with open(fullpath, "rb") as f:
        return base64.b64encode(f.read())

def convert_b64_string_to_file(s, outpath):
    with open(outpath, "wb") as f:
        f.write(base64.b64decode(s))

def random_N_digits(n, num):
  if n is None or n <= 0:
    n = 4
  if num is None or num == False:
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(n))
  return ''.join(random.choice(string.digits) for _ in range(n))
