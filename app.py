from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import flask_sitemap
import status

from datetime import timedelta
import logging
import secrets
import sys

from user_handling import get_db, load_users
import user_handling

from dotenv import load_dotenv
from config_loader import config

from api.api_blueprint import api_bp
from api.api_helpers import get_crepes

from classes import Crepes_Class, bcolors


load_users()

logging.basicConfig(filename="server.log", filemode="w", encoding="UTF-8", format="%(asctime)s %(levelname)s: %(message)s (%(filename)s; %(funcName)s; %(name)s)", level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout)) # Activate if logs should be print to console

flask_sitemap.config.SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True
flask_sitemap.config.SITEMAP_IGNORE_ENDPOINTS = "/sitemap.xml"

app = Flask(__name__)
ext = flask_sitemap.Sitemap(app=app)


app.register_blueprint(api_bp, url_prefix="/api")


load_dotenv()

app.secret_key = config.get("SECRETS", 'secret_key')

if app.secret_key is None:
    raise Exception("Es wurde kein secret_key definiert!")

app.permanent_session_lifetime = timedelta(minutes=5)


crêpes: list[Crepes_Class] | list[dict[str, str]] | None = get_crepes(as_dict=True)
if crêpes is None | type(crêpes) is list[Crepes_Class]:
    crêpes = []


shifts = []


global sales
sales: list = []


def valid_keys() -> list[str]:
    con, cur = get_db()
    cur.execute("SELECT s_key FROM secret_keys")
    keys = cur.fetchall()
    con.close()
    for i in range(len(keys)):
        keys[i] = keys[i][0]
    return keys


@app.route("/")
def serve_homepage():
    return render_template("index.jinja")


@app.route("/einstellungen")
def serve_einstellungen():
    try:
        if user_handling.authenticate_user(session, 10):
            return render_template("settings.jinja", crepes=crêpes)
        else:
            flash("settings")
            return redirect("/login")

    except Exception:
        flash("settings")
        return url_for("serve_login")


@app.route("/login", methods=["GET", "POST"])
def serve_login():

    if request.method == "GET":
        return render_template("login.jinja")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        comming_from = request.form["from"]

        logging.info(f"Username: {username} Password: {password}")
        user = user_handling.get_user_from_username_and_password(username, password)

        logging.info(str(user))

        if user is None:
            logging.warning(f"Could not log user {user} in!")
            return render_template("login.jinja")

        try:
            if user.current_key is None:
                secret_key = secrets.token_hex(100)
                session["secret"] = secret_key

                user.set_key(secret_key)
            else:
                secret_key = user.get_key()
                if not secret_key:
                    return redirect("/login")

            if user.priviledge == 10:

                logging.debug("User priviledge is 10")
                resp = redirect("/einstellungen")
                resp.set_cookie('secret', secret_key, 3600)
                session["secret"] = secret_key
                if comming_from == "shifts":
                    return redirect("/schichten")
                return redirect("/einstellungen")

            elif user.priviledge == 5:

                logging.debug("User priviledge is 5")
                resp = redirect("/schichten")
                resp.set_cookie('secret', secret_key, 3600)
                session["secret"] = secret_key
                return redirect("/schichten")

        except TypeError:
            return redirect("/login")

        return "", status.HTTP_403_FORBIDDEN
    else:
        return '', status.HTTP_405_METHOD_NOT_ALLOWED


@app.route("/schichten")
def serve_shifts():
    if user_handling.authenticate_user(session, 5):
        return render_template("shifts.jinja", shifts=shifts)
    else:
        flash("shifts")
        return redirect("/login")


@app.route("/dev")
def serve_dev():
    return render_template("development.jinja")


@app.route("/dashboard")
def serve_dashboard():
    if request.method != "GET":
        return '', status.HTTP_405_METHOD_NOT_ALLOWED

    return render_template("dashboard.jinja")


@app.route("/help")
def rick_roll():
    resp = redirect("https://youtu.be/dQw4w9WgXcQ")
    resp.headers.add("Du bist ein", "l'opfl")
    return resp  # Rickroll 😘


@app.route("/favicon.ico")
def serve_favicon():
    with open("static/assets/icons/favicon.ico", "rb") as f:
        data = f.read()
    resp = make_response(data)
    resp.headers.set("Content-Type", "image/x-icon")
    resp.status_code = status.HTTP_200_OK
    return resp


@app.route("/favicon_warn.ico")
def serve_warning_favicon():
    with open('static/assets/icons/favicon_warning.ico', "rb") as f:
        data = f.read()
    resp = make_response(data)
    resp.headers.set("Content-Type", "image/x-icon")
    resp.status_code = status.HTTP_200_OK
    return resp


@app.route("/init", methods=("GET", "POST"))
def initialisation():
    logging.debug("Sections: " + repr(config.sections()))
    if request.method == "GET":
        return render_template("init.jinja")

    elif request.method == "POST":
        if request.json:
            if request.json["auth"] == config.get("SECRETS", "auth_key"):
                return {
                    "status": "success",
                    "key": str(config.get("SECRETS", "auth_key"))
                    }
            else:
                return {"status": "failed", "error": "Code does not match"}

    return 'METHOD NOT ALLOWED', status.HTTP_405_METHOD_NOT_ALLOWED


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(*args, **kwargs):
    flash("NotFound", category="error")
    logging.critical("Flashed!")
    return redirect("/")


@app.before_request
def do_before_request_stuff():
    session.permanent = True

    logger = logging.getLogger("werkzeug")
    if request.path.startswith("/static"):
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.DEBUG)


def bad_request(e):
    if request.referrer:
        if "einstellungen" in request.referrer:
            return redirect("/einstellungen")
    return redirect("/")


app.register_error_handler(404, bad_request)


if __name__ == "__main__":
    logging.info("👋 app.py wurde ausgeführt!")

    if ('-p' in sys.argv) or ('--production' in sys.argv):

        import waitress
        print(bcolors.OKGREEN + "Production-Ready Server" + bcolors.ENDC)
        waitress.serve(app, host="0.0.0.0", port=80)

    elif ('-w' in sys.argv) or ('--waitress' in sys.argv):

        import waitress
        print(bcolors.OKCYAN + "Running with waitress" + bcolors.ENDC)
        waitress.serve(app, host="127.0.0.1", port=80)

    else:
        app.config['TEMPLATES_AUTO_RELOAD'] = True

        print(bcolors.WARNING + bcolors.BOLD + "Development server" + bcolors.ENDC)
        app.run(host='127.0.0.1', port=80, debug=True)
