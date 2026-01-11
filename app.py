#!/usr/bin/env python3

import os
import uuid
import flask

app = flask.Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if flask.request.method == "GET":
        return flask.render_template("index.html")
    elif flask.request.method == "POST":
        pass
    else:
        pass


@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    elif flask.request.method == "POST":
        return flask.render_template("login-successfully.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    elif flask.request.method == "POST":
        userid = flask.request.form["userid"]
        if not os.path.exists(f"users/{userid}"):
            os.mkdir(f"users/{userid}")
        file_uploaded = flask.request.files["avatar"]
        file_uploaded.save(f"users/{userid}/avatar.png")
        return flask.render_template("register-successfully.html")

@app.route("/users/<userid>", methods=["GET"])
def avatar(userid):
    return flask.send_from_directory(f"users/{userid}/", flask.request.args.get("avatar", ""))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
