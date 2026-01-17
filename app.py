#!/usr/bin/env python3

import flask
import helper_fun
import random
import secrets
from datetime import timedelta

app = flask.Flask(__name__)
app.secret_key = secrets.token_bytes()
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)




@app.route("/", methods=["GET"])
def index():
    print(">>>index")
    print(flask.session)
    print(flask.request.cookies)
    if flask.session.get("session_context") == "user":
        return flask.redirect(flask.url_for("user", userid=flask.session.get("userid")))
    else:
        return flask.render_template("index.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    print(">>>register")
    print(flask.session)
    print(flask.request.cookies)
    if flask.request.method == "GET":
        if flask.session.get("session_context") == "user":
            return flask.redirect(flask.url_for("user", userid=flask.session.get("userid")))
        else:
            flask.session["session_context"] = "register"
            if flask.session.get("contact_verified"):
                register_form = flask.session["data"]
                helper_fun.save_user_to_database(register_form)
                return flask.render_template("register-successfully.html", note="")
            else:
                return flask.render_template("register.html", note="")

    elif flask.request.method == "POST":
        register_form = flask.request.form
        error_count, check_res, register_form = helper_fun.check_register_form(register_form)
        if error_count == 0:
            flask.session["data"] = register_form
            flask.session["original_url"] = "/register"
            return flask.redirect(flask.url_for("verify"))
        
        else:
            note = ";".join([kk + ":" + ",".join(check_res[kk]) for kk in check_res if check_res[kk]])
            return flask.render_template("register.html", note=note)




@app.route("/verify", methods=["GET", "POST"])
def verify():
    print(">>>verify")
    print(flask.session)
    print(flask.request.cookies)
    if flask.request.method == 'GET':
        if flask.session.get("session_context") == "register":
            phone = flask.session["data"]["phone"]
            email = flask.session["data"]["email"]
            verify_code = format(random.randint(0, 999999), "06d")
            flask.session["verify_code"] = verify_code
            contact_type = "phone" if phone else ("email" if email else None)
            contact_address = phone or email
            helper_fun.send_verifying_code(contact_type, contact_address)
            return flask.render_template("verify.html", contact_type=contact_type, contact_address=contact_address)
 
        else:
            return flask.render_template("error.html"), 404

    elif flask.request.method == "POST":
        verify_form = flask.request.form
        if verify_form["button"] == "verify":
            #if verify_form["verify_code"] == flask.session["verify_code"]:
            if verify_form["verify_code"] == "123456":
                flask.session["contact_verified"] = True
                return flask.render_template("verify-successfully.html", redirect_url=flask.session["original_url"])
            else:
                contact_type = "phone" if phone else ("email" if email else None)
                contact_address = phone or email
                note = "verifying code is not corret"
                return flask.render_template("verify.html", contact_type=contact_type, contact_address=contact_address, note=note)


        elif verify_form["button"] == "resend":
            if flask.session["session_context"] == "register":
                phone = flask.session["data"]["phone"]
                email = flask.session["data"]["email"]
                verify_code = format(random.randint(0, 999999), "06d")
                flask.session["verify_code"] = verify_code
                contact_type = "phone" if phone else ("email" if email else None)
                contact_address = phone or email
                helper_fun.send_verifying_code(contact_type, contact_address)
                return flask.render_template("verify.html", contact_type=contact_type, contact_address=contact_address)
            
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
        if flask.session.get("session_context") == "register":
            flask.session.clear()
            flask.session["session_context"] = "login"
            return flask.render_template("login.html")
        elif flask.session.get("session_context") == "user":
            return flask.redirect(flask.url_for("user", userid=flask.session.get("userid")))
        else:
            flask.session["session_context"] = "login"
            return flask.render_template("login.html")

    elif flask.request.method == "POST":
        login_form = flask.request.form
        error_count, check_res, login_form = helper_fun.check_login(login_form)
        if error_count == 0:
            flask.session["session_id"] = secrets.token_urlsafe(32)
            flask.session["userid"] = login_form["userid"]
            flask.session["session_context"] = "user"
            resp = flask.redirect(flask.url_for("user", userid=login_form["userid"]))
            resp.set_cookie("userid", flask.session["userid"], httponly=True)
            resp.set_cookie("session_id", flask.session["session_id"], httponly=True)
            return resp
        
        else:
            note = ";".join([kk + ":" + ",".join(check_res[kk]) for kk in check_res if check_res[kk]])
            return flask.render_template("login.html", note=note)




@app.route("/logout")
def logout():
    print(">>>logout")
    print(flask.session)
    print(flask.request.cookies)
    flask.session.clear()
    resp = flask.make_response(flask.render_template("login.html"))
    resp.delete_cookie("userid")
    resp.delete_cookie("session_id")
    return resp




@app.route("/<userid>")
def user(userid):
    print(">>>user")
    print(flask.session)
    print(flask.request.cookies)
    if flask.session.get("session_context") == "user":
        if (flask.session.get("userid") and
            flask.request.cookies.get("userid") == flask.session.get("userid") and
            userid == flask.session.get("userid") and 
            flask.session.get("session_id") and
            flask.request.cookies.get("session_id") == flask.session.get("session_id")):
            return flask.render_template("user.html", userid=userid)
        else:
            return flask.render_template("error.html"), 404
    else:
        return flask.redirect(flask.url_for("login"))




@app.route("/test")
def test():
    resp = flask.make_response("", 204)
    resp.set_cookie("my_cookie", "hello2")
    return resp



if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
