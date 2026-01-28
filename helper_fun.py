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
    error, ent = db.query("user_identity", "userid", userid)
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


def add_user(userid, nickname, phone, email, password, signup_time):
    salt, password_hash = hash_password(password)
    signup_time = change_datetime_to_integer(signup_time)
    status = 0

    db = database.Sqlite3_DB("auth/users.db")
    error = db.insert("user_identity",
               (userid, nickname, phone, email, signup_time,
                salt, password_hash, status),
               ("userid", "nickname", "phone", "email", "register_time",
                "salt", "password_hash", "status"))
    db.disconnect()
    return error


def delete_user(userid):
    db = database.Sqlite3_DB("auth/users.db")
    error = db.delete("user_identiy", "userid", userid)
    return error


def add_signin_signout_entry(userid, action, action_time, action_result):
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
    if not session_id:
        return None

    db = database.Sqlite3_DB("auth/session.db")
    error, ents = db.query("live_session", "session_id", session_id)
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


def check_signup_form(signup_form):
    userid = signup_form["userid"]
    nickname = signup_form["nickname"] if signup_form["nickname"] else \
        signup_form["userid"]
    contact = signup_form["contact"]
    password = signup_form["password"]
    password_confirm = signup_form["password-confirm"]

    error = {
        "userid": [],
        "nickname": [],
        "contact": [],
        "password": []
    }
    signup_form_new = {}

    if not (len(userid) >= 1 and len(userid) <= 16):
        error["userid"].append("the format of userid is wrong")
    elif if_user_exists(userid):
        error["userid"].append("the userid has been used")
    signup_form_new["userid"] = userid

    if not (len(nickname) >= 1 and len(nickname) <= 16):
        error["nickname"].append("the format of nickname is wrong")
    else:
        signup_form_new["nickname"] = nickname

    if len(contact) == 11 and contact[0] == '1' and contact.isdigit():
        signup_form_new["phone"] = contact
        signup_form_new["email"] = None
    elif email_re_tmp.match(contact):
        signup_form_new["email"] = contact
        signup_form_new["phone"] = None
    else:
        error["contact"].append("the format of contact address is wrong")
    
    if signup_form_new["phone"] and if_phone_used(signup_form_new["phone"]):
        error["contact"].append("the phone number has been used by other")
    
    if signup_form_new["email"] and if_email_used(signup_form_new["email"]):
        error["contact"].append("the email has been used by other")

    if password != password_confirm:
        error["password"].append("passwords inputted not match each other")

    if len(password) < 9:
        error["password"].append("the length of password is less than 9")
    
    signup_form_new["password"] = password

    error = {key: error[key] for key in error if error[key]}

    return error, signup_form_new


def check_signin_form(signin_form):
    error = {
        "userid": [],
        "password": []
    }

    userid = signin_form["userid"]
    password = signin_form["password"]

    signin_form_new = {
        "userid": userid,
        "password": password
    }

    db = database.Sqlite3_DB("auth/users.db")
    if not if_user_exists(userid):
        error["userid"].append("user-not-exists")
    
    else:
        error_db, [(salt, password_hash)] = db.query("user_identity", "userid", userid,
                                       ("salt", "password_hash"))
        password_ok = compare_password(password_hash_stored=password_hash, salt=salt, password=password)
        if not password_ok:
            error["password"].append("password-not-correct")
    error = {key: error[key] for key in error if error[key]}
    
    return error, signin_form_new
    

def send_verification_code(contact_type, contact_address):
    pass


def check_user_photo(userid, photo_name):
    user_photo_path = "users"
    photo_path = os.path.join(user_photo_path, userid, photo_name)
    if os.path.exists(photo_path):
        return photo_path
    else:
        return None


