import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/login.html")
def login():
    return flask.render_template("login.html")


@app.route("/register.html")
def register():
    return flask.render_template("register.html")