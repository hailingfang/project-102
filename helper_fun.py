import re
import database
import os
import hashlib
import hmac
import datetime
import uuid

email_re_tmp = re.compile(r"[\w.]+@(?:\w|\.)+\.(com|edu|cn|org)")


def change_datetime_to_integer(time_in):
    time_in = str(time_in.year)[2:] + format(time_in.month, "02d") + \
        format(time_in.day, "02d") + format(time_in.hour, "02d") + \
        format(time_in.minute, "02d") + format(time_in.second, "02d")
    time_in = int(time_in)
    return time_in


def hash_password(password, algo):
    if algo == 'hmac':
        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
        return algo, salt, password_hash
    else:
        return None, None, None


def compare_password(password_hash_stored, salt, password, algo):
    if algo == "hmac":
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 1000_000)
        return hmac.compare_digest(new_key, password_hash_stored)
    else:
        return False


def get_contact_type_and_address(phone, email):
    contact_type = "phone" if phone else ("email" if email else None)
    contact_address = phone or email
    return contact_type, contact_address


def if_user_id_exists(user_id):
    db = database.Sqlite3_DB("data/users.db")
    error, ent = db.query("user_profile", "user_id", user_id)
    db.disconnect()
    if ent:
        return True
    else:
        return False


def if_phone_used(phone):
    db = database.Sqlite3_DB("data/users.db")
    error, ent = db.query("user_credentials", "phone", phone, ("phone", "phone_verified"))
    db.disconnect()

    if ent and ent[0][1]:
        return True
    else:
        return False   


def if_email_used(email):
    db = database.Sqlite3_DB("data/users.db")
    error, ent = db.query("user_identity", "email", email, ("email", "email_verified"))
    db.disconnect()

    if ent and ent[0][1]:
        return True
    else:
        return False


def add_user(user_id, nickname, phone, email, password):
    user_id_db = str(uuid.uuid4())
    algo, salt, password_hash = hash_password(password=password, algo="hmac")
    signup_time = change_datetime_to_integer(datetime.datetime.now())
    phone_verified = 1 if phone else 0
    email_verified = 1 if email else 0

    users_db = database.Sqlite3_DB("data/users.db")
    error1 = users_db.insert("user_identity",
                            (user_id_db, "active", signup_time),
                            ("user_id_db", "status", "created_at"))

    error2 = users_db.insert("user_credentials",
                            (user_id_db, email, email_verified, phone, phone_verified,
                            algo, salt, password_hash, signup_time),
                            ("user_id_db", "email", "email_verified", "phone", "phone_verified",
                            "password_algo", "password_salt", "password_hash", "created_at"))

    error3 = users_db.insert("user_profile",
                            (user_id_db, user_id, nickname, signup_time),
                            ("user_id_db", "user_id", "nickname", "created_at"))

    users_db.disconnect()
    
    return error1 or error2 or error3


def get_user_id_by_user_id_db(user_id_db):
    db = database.Sqlite3_DB("data/users.db")
    error, ent = db.query("user_profile", "user_id_db", user_id_db, ("user_id"))
    if not error and ent:
        user_id = ent[0]
        return user_id
    else:
        return None


def get_user_id_db_by_user_id(user_id):
    db = database.Sqlite3_DB("data/users.db")
    error, ent = db.query("user_profile", "user_id", user_id, ("user_id_db"))
    if not error and ent:
        user_id_db = ent[0]
        return user_id_db
    else:
        return None


def delete_user(user_id_db):
    delete_time = change_datetime_to_integer(datetime.datetime.now())
    db = database.Sqlite3_DB("data/users.db")
    error1 = db.update("user_identity", "user_id_db", user_id_db, 
                       ("status", "deleted_at"), ("deleted", delete_time))
    error2 = db.delete("user_credentials", "user_id_db", user_id_db)
    error3 = db.delete("user_profile", "user_id_db", user_id_db)

    return error1 or error2 or error3


def add_auth_log(user_id_db, action, action_result):
    action_time = change_datetime_to_integer(datetime.datetime.now())      

    db = database.Sqlite3_DB("data/log.db")
    error = db.insert("auth_log",
                      (user_id_db, action, action_result, action_time),
                      ("user_id_db", "action", "action_result", "created_at"))
    db.disconnect()
    return error


def add_session_entry(session_id, user_id_db):
    created_at = change_datetime_to_integer(datetime.datetime.now())
    expire_time = change_datetime_to_integer(created_at + datetime.timedelta(days=30))
    
    db = database.Sqlite3_DB("data/sessions.db")
    error = db.insert("user_session",
                      (session_id, user_id_db, created_at, expire_time),
                      ("session_id", "user_id_db", "created_at", "expires_at"))
    db.disconnect()
    return error


def delete_session(session_id):
    db = database.Sqlite3_DB("data/sessions.db")
    error = db.delete("user_session", "session_id", session_id)
    db.disconnect()
    return error


def check_session(session_id):
    if not session_id:
        return None

    db = database.Sqlite3_DB("data/sessions.db")
    error, ents = db.query("user_session", "session_id", session_id, ("session_id", "user_id_db", "expires_at"))
    if ents:
        session_id, user_id_db, expires_at = ents[0]
    else:
        return None
    
    time_now = change_datetime_to_integer(datetime.datetime.now())
    if time_now > expires_at:
        delete_session(session_id)
        return None
    else:
        return user_id_db


def check_signup_form(signup_form):
    user_id = signup_form["user_id"]
    nickname = signup_form["nickname"] if signup_form["nickname"] else \
        signup_form["user_id"]
    contact = signup_form["contact"]
    password = signup_form["password"]
    password_confirm = signup_form["password_confirm"]

    error = {
        "user_id": [],
        "nickname": [],
        "contact": [],
        "password": []
    }
    signup_form_new = {}

    if not (len(user_id) >= 1 and len(user_id) <= 16):
        error["userid"].append("the format of userid is wrong")
    elif if_user_id_exists(user_id):
        error["userid"].append("the userid has been used")
    signup_form_new["user_id"] = user_id

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
        "user_id": [],
        "password": []
    }

    user_id = signin_form["user_id"]
    password = signin_form["password"]

    signin_form_new = {
        "user_id": user_id,
        "password": password
    }
    user_id_db = get_user_id_db_by_user_id(user_id)

    if user_id_db:
        db = database.Sqlite3_DB("data/users.db")
        error, ents = db.query("user_identity", "user_id_db", user_id_db, ("status"))
        if not (ents and ents[0][0] == "active"):
            error["user_id"].append("user-not-exists")
        error, [(algo, password_salt, password_stored)] = db.query("user_credentials", 
            "user_id_db", user_id_db, ("password_algo", "password_salt", "password_hash"))
    
        compare_res = compare_password(password_hash_stored=password_stored,
                     password_salt=password_salt,
                     password=password,
                     algo=algo)
    
        if not compare_res:
            error["password"].append("password error")
    
    else:
        error["user_id"].append("user-not-exists")

    error = {key: error[key] for key in error if error[key]}
    
    return error, signin_form_new
    

def send_verification_code(contact_type, contact_address):
    pass


def check_user_photo(userid, photo_name):
    pass

def query_user_profile(user_id_db):
    db = database.Sqlite3_DB("data/users.db")
    query_colums = ("user_id", "nickname", "avatar_id", "gender", "birth_date", "city", "bio", "words")
    error, ents = db.query("user_profile", "user_id_db", user_id_db, query_colums)
    if not error and ents:
        profile = ents[0]
        profile = {ele[0]: ele[1] for ele in zip(query_colums, profile)}
        return profile
    else:
        return {}
