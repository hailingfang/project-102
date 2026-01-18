#!/usr/bin/env python3

import flask
import helper_fun
import random
import secrets
import datetime


app = flask.Flask(__name__)
app.secret_key = secrets.token_bytes()
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)


@app.route("/", methods=["GET"])
def index():
    print(">>>index")
    print(flask.session)
    print(flask.request.cookies)

    if flask.request.cookies.get("session_id"):
        userid = helper_fun.check_session(flask.request.cookies.get("session_id"))
        if userid:
            #show a index page, that has user login infor. show some other information
            #download mobile app, jump to /user webpage.
            return flask.render_template("index.html", userid=userid)
        else:
            resp = flask.make_response(flask.render_template("index.html", userid=""))
            resp.delete_cookie("session_id")
            return resp
    else:
        return flask.render_template("index.html", userid="")


@app.route("/register", methods=["GET", "POST"])
def register():
    print(">>>register")
    print(flask.session)
    print(flask.request.cookies)

    if flask.request.method == "GET":
        if flask.session.get("verify_status") == "OK":
            register_form = flask.session["register_data"]
            userid = register_form["userid"]
            nickname = register_form["nickname"]
            phone = register_form["phone"]
            email = register_form["email"]
            password = register_form["password"]
            helper_fun.add_user(userid, nickname, phone, email, password,
                                datetime.datetime.now())
            flask.session.clear()
            return flask.render_template("register-successfully.html")
        
        elif flask.request.cookies.get("session_id"):
            return flask.redirect(flask.url_for("index"))
        
        else:
            return flask.render_template("register.html", note="")

    elif flask.request.method == "POST":
        register_form = flask.request.form
        error_count, check_res, register_form = \
            helper_fun.check_register_form(register_form)
        if error_count == 0:
            flask.session["context"] = "register"
            flask.session["register_data"] = register_form
            contact_type, contact_address = \
                helper_fun.get_contact_type_and_address(register_form["phone"],
                                                        register_form["email"])
            flask.session["verigy_data"] = {"contact_type": contact_type,
                                     "contact_address": contact_address}
            return flask.redirect(flask.url_for("verify"))
        
        else:
            note = ";".join([kk + ":" + ",".join(check_res[kk]) 
                             for kk in check_res if check_res[kk]])
            return flask.render_template("register.html", note=note)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    print(">>>verify")
    print(flask.session)
    print(flask.request.cookies)

    if flask.request.method == 'GET':
        if flask.session.get("context") == "register":
            contact_type = flask.session["verify_data"]["contact_type"]
            contact_address = flask.session["verify_data"]["contact_address"]
            verify_code = format(random.randint(0, 999999), "06d")
            flask.session["verify_code"] = verify_code
            helper_fun.send_verifying_code(contact_type, contact_address)
            return flask.render_template("verify.html",
                                         contact_type=contact_type,
                                         contact_address=contact_address)
 
        else:
            return flask.render_template("error.html"), 404

    elif flask.request.method == "POST":
        if flask.session.get("context") == "register":
            verify_form = flask.request.form
            if verify_form["button"] == "verify":
                if verify_form["verify_code"] == "123456": #flask.session["verify_code"]
                    flask.session["verify_status"] = 'OK'
                    return flask.render_template("verify-successfully.html",
                                        redirect_url="/register")
                else:
                    contact_type = flask.session["verify_data"]["contact_type"]
                    contact_address = flask.session["verify_data"]["contact_address"]
                    note = "verifying code is not corret"
                    return flask.render_template("verify.html",
                                                contact_type=contact_type,
                                                contact_address=contact_address,
                                                note=note)

            elif verify_form["button"] == "resend":
                if flask.session["session_context"] == "register":
                    contact_type = flask.session["verify_data"]["contact_type"]
                    contact_address = flask.session["verify_data"]["contact_address"]
                    verify_code = format(random.randint(0, 999999), "06d")
                    flask.session["verify_code"] = verify_code
                    helper_fun.send_verifying_code(contact_type, contact_address)
                    return flask.render_template("verify.html",
                                                contact_type=contact_type,
                                                contact_address=contact_address)
                else:
                    return flask.render_template("error.html"), 404
            else:
                return flask.render_template("error.html"), 404
        else:
            return flask.render_template("error.html"), 404


@app.route("/login", methods=["GET", "POST"])
def login():
    print(">>>login")
    print(flask.session)
    print(flask.request.cookies)

    if flask.request.method == "GET":
        if flask.request.cookies.get("session_id"):
            return flask.redirect(flask.url_for("user"))

        else:
            return flask.render_template("login.html")

    elif flask.request.method == "POST":
        login_form = flask.request.form
        error_count, check_res, login_form = helper_fun.check_login_form(login_form)
        if error_count == 0:
            userid = login_form["userid"]
            session_id = secrets.token_urlsafe(32)
            helper_fun.add_login_logout_entry(userid, "login",
                                              datetime.datetime.now(), 0)
            helper_fun.add_session_entry(session_id, 
                                         userid,
                                         datetime.datetime.now() +
                                         datetime.timedelta(days=30))


            flask.session.clear()
            resp = flask.redirect(flask.url_for("user"))
            resp.set_cookie("session_id", session_id, httponly=True)
            return resp
        
        else:
            note = ";".join([kk + ":" + ",".join(check_res[kk]) for
                             kk in check_res if check_res[kk]])
            return flask.render_template("login.html", note=note)


@app.route("/logout")
def logout():
    print(">>>logout")
    print(flask.session)
    print(flask.request.cookies)
    
    if flask.request.cookies.get("session_id"):
        helper_fun.delete_session(flask.request.cookies.get("session_id"))
    flask.session.clear()
    
    resp = flask.make_response(flask.render_template("index.html", userid=""))
    resp.delete_cookie("session_id")
    return resp


@app.route("/user")
def user():
    print(">>>user")
    print(flask.session)
    print(flask.request.cookies)

    if flask.request.cookies.get("session_id"):
        userid = helper_fun.check_session(flask.request.cookies.get("session_id"))
        if userid:
            return flask.render_template("user.html", userid=userid)
        else:
            helper_fun.delete_session(flask.request.cookies.get("session_id"))
            return flask.redirect(flask.url_for("login"))
    else:
        return flask.redirect(flask.url_for("login"))


@app.route("/get-user-photo/<userid>/<photo_name>")
def get_user_photo(userid, photo_name):
    #Check authorization

    photo_path = helper_fun.check_user_photo(userid, photo_name)
    if photo_path:
        return flask.send_file(photo_path)
    else:
        return ""


@app.route("/test")
def test():
    return flask.render_template("test.html")



if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
