#!/usr/bin/env python3

from flask import Flask, request, session, render_template, make_response, redirect, url_for, send_file
import helper_fun
import random
import secrets
import datetime


app = Flask(__name__)
app.secret_key = secrets.token_bytes()
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)


@app.route("/", methods=["GET"])
def index():
    print(">>>index")
    print(session)
    print(request.cookies)

    session_id = request.cookies.get("session_id")

    if session_id:
        userid = helper_fun.check_session(session_id)
        if userid:
            return render_template("index.html", userid=userid)
        else:
            resp = make_response(render_template("index.html", userid=None))
            resp.delete_cookie("session_id")
            return resp
    else:
        return render_template("index.html", userid=None)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    print(">>>signup")
    print(session)
    print(request.cookies)

    if request.method == "GET":
        if request.cookies.get("session_id"):
            return redirect(url_for("user"))
        elif session.get("verify_signup") == "OK":
            signup_form = session["signup_form"]
            helper_fun.add_user(userid=signup_form["userid"],
                                nickname=signup_form["nickname"],
                                phone=signup_form["phone"],
                                email=signup_form["email"],
                                password=signup_form["password"],
                                signup_time=datetime.datetime.now())
            session.clear()
            return render_template("signup-successfully.html")
        else:
            return render_template("signup.html", error={})

    elif request.method == "POST":
        signup_form = request.form
        error, signup_form = \
            helper_fun.check_signup_form(signup_form)
        if not error:
            session["verify_context"] = "signup"
            session["signup_form"] = signup_form
            contact_type, contact_address = \
                helper_fun.get_contact_type_and_address(signup_form["phone"],
                                                        signup_form["email"])
            session["contact_type"] = contact_type
            session["contact_address"] = contact_address
            return redirect(url_for("verify"))
        
        else:
            return render_template("signup.html", error=error)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    print(">>>verify")
    print(session)
    print(request.cookies)

    if request.method == 'GET':
        if session.get("verify_context") == "signup":
            contact_type = session["contact_type"]
            contact_address = session["contact_address"]
            verify_code = format(random.randint(0, 999999), "06d")
            session["verify_code"] = verify_code
            helper_fun.send_verification_code(contact_type, contact_address)
            return render_template("verify.html",
                                         contact_type=contact_type,
                                         contact_address=contact_address)
 
        else:
            return render_template("error.html"), 404

    elif request.method == "POST":
        if session.get("verify_context") == "signup":
            verify_form = request.form
            if verify_form["button"] == "verify":
                if verify_form["verify_code"] == "123456": #flask.session["verify_code"]
                    session["verify_signup"] = 'OK'
                    return render_template("verify-successfully.html",
                                        redirect_url="/signup")
                else:
                    contact_type = session["contact_type"]
                    contact_address = session["contact_address"]
                    error = "verifying code is not corret"
                    return render_template("verify.html",
                                            contact_type=contact_type,
                                            contact_address=contact_address,
                                            error=error)

            elif verify_form["button"] == "resend":
                contact_type = session["contact_type"]
                contact_address = session["contact_address"]
                verify_code = format(random.randint(0, 999999), "06d")
                session["verify_code"] = verify_code
                helper_fun.send_verification_code(contact_type, contact_address)
                return render_template("verify.html",
                                        contact_type=contact_type,
                                        contact_address=contact_address)
            
            else:
                return render_template("error.html"), 404

        else:
            return render_template("error.html"), 404


@app.route("/signin", methods=["GET", "POST"])
def signin():
    print(">>>signin")
    print(session)
    print(request.cookies)

    if request.method == "GET":
        if request.cookies.get("session_id"):
            return redirect(url_for("user"))

        else:
            return render_template("signin.html", error={})

    elif request.method == "POST":
        signin_form = request.form
        error, signin_form = helper_fun.check_signin_form(signin_form)

        if not error:
            print("+++++++", error)
            userid = signin_form["userid"]
            session_id = secrets.token_urlsafe(32)
            helper_fun.add_signin_signout_entry(userid=userid,
                                                action="signin",
                                                action_time=datetime.datetime.now(),
                                                action_result=0)
            helper_fun.add_session_entry(session_id, 
                                         userid,
                                         datetime.datetime.now() +
                                         datetime.timedelta(days=30))

            session.clear()
            resp = make_response(redirect(url_for("user")))
            resp.set_cookie("session_id", session_id, httponly=True)
            return resp
        
        else:
            return render_template("signin.html", error=error)


@app.route("/signout")
def signout():
    print(">>>signout")
    print(session)
    print(request.cookies)
    
    session_id = request.cookies.get("session_id")
    if session_id:
        userid = helper_fun.check_session(session_id)
        if userid:
            helper_fun.add_signin_signout_entry(userid=userid,
                                                action="signout",
                                                action_time=datetime.datetime.now(),
                                                action_result=0)
            helper_fun.delete_session(session_id)
    session.clear()
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("session_id")
    return resp


@app.route("/user")
def user():
    print(">>>user")
    print(session)
    print(request.cookies)

    if request.cookies.get("session_id"):
        userid = helper_fun.check_session(request.cookies.get("session_id"))
        if userid:
            return render_template("user.html", userid=userid)
        else:
            session.clear()
            resp = make_response(redirect(url_for("signin")))
            resp.delete_cookie("session_id")
            return resp
    else:
        return redirect(url_for("signin"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
