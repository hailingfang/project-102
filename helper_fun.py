import re
import database
import os
import hashlib
import hmac
import datetime

email_re_tmp = re.compile(r"[\w.]+@(?:\w|\.)+\.(com|edu|cn|org)")


def change_datetime_to_integer(time_in):
    time_in = str(time_in.year)[2:] + format(time_in.month, "02d") + \
        format(time_in.day, "02d") + format(time_in.hour, "02d") + \
        format(time_in.minute, "02d") + format(time_in.second, "02d")
    time_in = int(time_in)
    return time_in


def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
    return salt, password_hash


def compare_password(password_hash_stored, salt, password):
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
    return hmac.compare_digest(new_key, password_hash_stored)


def get_contact_type_and_address(phone, email):
    contact_type = "phone" if phone else ("email" if email else None)
    contact_address = phone or email

    return contact_type, contact_address


def if_user_exists(userid):
    db = database.Sqlite3_DB("auth/users.db")
    ent, error = db.query("user_identity", "userid", userid)
    db.disconnect()
    if ent:
        return True
    else:
        return False


def if_phone_used(phone):
    db = database.Sqlite3_DB("auth/users.db")
    ent, error = db.query("user_identity", "phone", phone)
    db.disconnect()
    if ent:
        return True
    else:
        return False


def if_email_used(email):
    db = database.Sqlite3_DB("auth/users.db")
    ent, error = db.query("user_identity", "email", email)
    db.disconnect()
    if ent:
        return True
    else:
        return False


def add_user(userid, nickname, phone, email, password, register_time):
    salt, password_hash = hash_password(password)
    register_time = change_datetime_to_integer(register_time)
    status = 0

    db = database.Sqlite3_DB("auth/users.db")
    error = db.insert("user_identity",
               (userid, nickname, phone, email, register_time,
                salt, password_hash, status),
               ("userid", "nickname", "phone", "email", "register_time",
                "salt", "password_hash", "status"))
    db.disconnect()
    return error


def delete_user(userid):
    db = database.Sqlite3_DB("auth/users.db")
    error = db.delete("user_identiy", "userid", userid)
    return error


def add_login_logout_entry(userid, action, action_time, action_result):
    action_time = change_datetime_to_integer(action_time)      

    db = database.Sqlite3_DB("auth/log.db")
    error = db.insert("login_logout_log",
                      (userid, action, action_time, action_result),
                      ("userid", "action", "action_time", "action_result"))
    db.disconnect()
    return error


def add_session_entry(session_id, userid, expire_time):
    expire_time = change_datetime_to_integer(expire_time)
    
    db = database.Sqlite3_DB("auth/session.db")
    error = db.insert("live_session",
                      (session_id, userid, expire_time),
                      ("session_id", "userid", "expire_time"))
    db.disconnect()
    return error


def delete_session(session_id):
    db = database.Sqlite3_DB("auth/session.db")
    error = db.delete("live_session", "session_id", session_id)
    db.disconnect()
    return error


def check_session(session_id):
    db = database.Sqlite3_DB("auth/session.db")
    ents, error = db.query("live_session", "session_id", session_id)
    if ents:
        session_id, userid, expire_time = ents[0]
    else:
        return None
    
    time_now = change_datetime_to_integer(datetime.datetime.now())
    if time_now > expire_time:
        delete_session(session_id)
        return None
    else:
        return userid


def check_register_form(register_form):
    userid = register_form["userid"]
    nickname = register_form["nickname"] if register_form["nickname"] else \
        register_form["userid"]
    
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

    if not (len(userid) >= 1 and len(userid) <= 16):
        error_count += 1
        check_res["userid"].append("format-error")
    elif if_user_exists(userid):
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
    
    if phone and if_phone_used(phone):
        error_count += 1
        check_res["phone-email"].append("phone-used")
    
    if email and if_email_used(email):
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


def check_login_form(login_form):
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

    db = database.Sqlite3_DB("auth/users.db")
    if not if_user_exists(userid):
        error_count += 1
        check_res["userid"].append("userid-not-registered")
    
    else:
        [(salt, password_hash)], error = db.query("user_identity", "userid", userid,
                                       ("salt", "password_hash"))
        password_ok = compare_password(password_hash_stored=password_hash, salt=salt, password=password)
        if not password_ok:
            error_count += 1
            check_res["password"].append("password-not-correct")
    
    return error_count, check_res, new_form
    

def send_verifying_code(contact_type, contact_address):
    pass


def check_user_photo(userid, photo_name):
    user_photo_path = "users"
    photo_path = os.path.join(user_photo_path, userid, photo_name)
    if os.path.exists(photo_path):
        return photo_path
    else:
        return None


