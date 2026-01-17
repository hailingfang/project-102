import re
import database
import os
import hashlib
import hmac

email_re_tmp = re.compile(r"[\w.]+@(?:\w|\.)+\.(com|edu|cn|org)")

def check_register_form(register_form):
    userid = register_form["userid"]
    nickname = register_form["nickname"]
    phone_email = register_form["phone-email"]
    password = register_form["password"]
    password_confirm = register_form["password-confirm"]

    error_count = 0
    check_res = {
        "userid": [],
        "nickname": [],
        "phone-email": [],
        "email": [],
        "password": []
    }

    db = database.Sqlite3_DB("users.db")

    if not (len(userid) >= 1 and len(userid) <= 16):
        error_count += 1
        check_res["userid"].append("format-error")
    if db.if_userid_used(userid):
        error_count += 1
        check_res["userid"].append("userid-used")

    if not (len(nickname) >= 1 and len(nickname) <= 16):
        error_count += 1
        check_res["nickname"].append("format-error")
    
    phone = None
    email = None
    if len(phone_email) == 11 and phone_email[0] == '1' and phone_email.isdigit():
        phone = phone_email
    elif email_re_tmp.match(phone_email):
        email = phone_email
    else:
        error_count += 1
        check_res["phone-email"].append("format-error")
    
    if phone and db.if_phone_used(phone):
        error_count += 1
        check_res["phone-email"].append("phone-used")
    
    if email and db.if_email_used(email):
        error_count += 1
        check_res["phone-email"].append("email-used")

    if password != password_confirm:
        error_count += 1
        check_res["password"].append("not-match")

    if len(password) < 9:
        error_count += 1
        check_res["password"].append("format-error")
    
    new_form = {"userid": userid, 
                "nickname": nickname,
                "phone": phone, 
                "email": email,
                "password": password}

    return error_count, check_res, new_form


def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
    return salt, password_hash


def compare_password(password_hash_stored, salt, password):
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
    return hmac.compare_digest(new_key, password_hash_stored)


def save_user_to_database(register_form):
    userid = register_form["userid"]
    nickname = register_form["nickname"]
    phone = register_form["phone"]
    email = register_form["email"]
    password = register_form["password"]
    salt, password_hash = hash_password(password)
    db = database.Sqlite3_DB("users.db")
    db.add_user(userid=userid,
                nickname=nickname,
                phone=phone,
                email=email,
                salt=salt,
                password_hash=password_hash,
                status=0)
    db.disconnect()


def check_login(login_form):
    error_count = 0
    check_res = {
        "userid": [],
        "password": []
    }

    userid = login_form["userid"]
    password = login_form["password"]

    new_form = {
        "userid": userid,
        "password": password
    }

    db = database.Sqlite3_DB("users.db")
    if not db.if_userid_used(userid):
        error_count += 1
        check_res["userid"].append("userid-not-registered")
    
    else:
        user_infor = db.get_user(userid)
        salt, password_hash = user_infor[-3], user_infor[-2]
        password_ok = compare_password(password_hash_stored=password_hash, salt=salt, password=password)
        if not password_ok:
            error_count += 1
            check_res["password"].append("password-not-correct")
    
    return error_count, check_res, new_form
    


def send_verifying_code(contact_type, contact_address):
    pass