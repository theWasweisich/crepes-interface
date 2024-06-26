import json
from setup_logger import access_logger, server_handler, werkzeug_handler, root_logger
import os

from datetime import datetime
from flask import (
    Flask,
    flash,
    # make_response,
    redirect,
    request,
    session,
    url_for,
    send_from_directory,
)
from flask.logging import default_handler
import flask_sitemap
import status

import logging
import secrets
# import sys

from mysql_handler._database_handling import getCrepeDB
import user_handling

from config_loader import config
from utilities.arg_handler import parser

from api.api_blueprint import get_api_bp

from classes import bcolors
import atexit


api_bp = get_api_bp()

os.chdir(os.path.dirname(__file__))  # Set current working directory to the app/ folder, in order for relative paths to work :)


class ArgumentError(Exception):
    pass


args = parser.parse_args()
if args.runWaitress and args.runProd:
    raise ArgumentError("Es kann nicht gleichzeitig der Waitress-Modus und Produktionsmodus aktiviert sein!")

if args.verbose:
    access_logger.addHandler(logging.StreamHandler())


# logging.getLogger().addHandler(logging.StreamHandler(sys.stdout)) # Activate if logs should be print to console

access_logger.removeHandler(logging.FileHandler("./logs/server.log", "w", encoding="UTF-8"))

flask_sitemap.config.SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS = True
flask_sitemap.config.SITEMAP_IGNORE_ENDPOINTS = "/sitemap.xml"

app = Flask(__name__)
ext = flask_sitemap.Sitemap(app=app)

app.logger.removeHandler(default_handler)
app.logger.addHandler(server_handler)
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

app.register_blueprint(api_bp, url_prefix="/api")

try:
    app.secret_key = config.get("SECRETS", 'secret_key')
except Exception:
    logging.critical(f"Key: {config.sections()}")
    raise SystemExit("Die Konfiguration spinnt!")

if app.secret_key is None:
    raise SystemExit("Es wurde kein secret_key definiert! Bitte first_configuration.py ausführen!")


shifts = []


global sales
sales: list = []


def valid_keys() -> list[str]:
    with getCrepeDB() as (_, cur):
        cur.execute("SELECT s_key FROM secret_keys")
        keys = cur.fetchall()
    for i in range(len(keys)):
        keys[i] = keys[i][0]
    return keys


@app.route("/")
def serve_homepage():
    return send_from_directory("./static/html/", "index.html")


@app.route("/einstellungen")
def serve_einstellungen():
    try:
        if user_handling.authenticate_user(session, 10):
            return send_from_directory("./static/html/", "settings.html")
        else:
            return redirect("/login")

    except Exception:
        return url_for("serve_login")


@app.route("/login", methods=["GET", "POST"])
def serve_login():

    if request.method == "GET":
        return send_from_directory("./static/html/", "login.html")

    elif request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return redirect("/login?login=failed", status.HTTP_303_SEE_OTHER)
        if not password:
            return redirect("/login?login=failed", status.HTTP_303_SEE_OTHER)

        user = user_handling.get_user_from_username_and_password(username, password)
        app.logger.warning(f"User: {user=}")

        if user is None:
            logging.warning(f"Failed Login Attempt! User: {user}")
            return redirect("/login?login=failed", status.HTTP_303_SEE_OTHER)

        try:
            if user.current_key is None:
                secret_key = secrets.token_bytes(100)

                session["secret"] = secret_key
                user.set_key(secret_key)
                assert user.get_key() == secret_key

            if user.priviledge == 10:

                resp = redirect("/einstellungen")
                resp.set_cookie(key='secret', value=str(user.current_key), max_age=3600)
                session["secret"] = user.current_key
                return resp

            elif user.priviledge == 5:

                resp = redirect("/schichten")
                resp.set_cookie(key='secret', value=str(user.current_key), max_age=3600)
                session["secret"] = user.current_key
                return resp

        except TypeError:
            return redirect("/login")

        return "", status.HTTP_403_FORBIDDEN
    else:
        return '', status.HTTP_405_METHOD_NOT_ALLOWED


@app.route("/schichten")
def serve_shifts():
    return redirect("/")

    # if user_handling.authenticate_user(session, 5):
    #     return render_template("shifts.jinja", shifts=shifts)
    # else:
    #     flash("shifts")
    #     return redirect("/login")


@app.route("/dev")
def serve_dev():
    return send_from_directory("./static/html/", "development.html")


@app.route("/dashboard")
def serve_dashboard():
    if request.method != "GET":
        return '', status.HTTP_405_METHOD_NOT_ALLOWED

    return send_from_directory("./static/html/", "dashboard.html")


@app.route("/help")
def rick_roll():
    resp = redirect("https://youtu.be/dQw4w9WgXcQ")
    resp.headers.add("Du bist ein", "l'opfl")
    return resp  # Rickroll 😘


@app.route("/favicon.ico")
def serve_favicon():
    # with open("./static/assets/icons/favicon.ico", "rb") as f:
    #     data = f.read()
    # resp = make_response(data)

    static_folder = app.static_folder if app.static_folder is not None else "ERROR"

    resp = send_from_directory(static_folder, "assets/icons/favicon.ico")
    resp.headers.set("Content-Type", "image/x-icon")
    resp.status_code = status.HTTP_200_OK
    return resp


@app.route("/favicon_warn.ico")
def serve_warning_favicon():
    # with open('static/assets/icons/favicon_warning.ico', "rb") as f:
    #     data = f.read()
    # resp = make_response(data)
    static_folder = app.static_folder if app.static_folder is not None else "ERROR"

    resp = send_from_directory(static_folder, "assets/icons/favicon_warning.ico")
    resp.headers.set("Content-Type", "image/x-icon")
    resp.status_code = status.HTTP_200_OK
    return resp


@app.route("/init", methods=("GET", "POST"))
def initialisation():
    # root_logger.critical("Sections: " + repr(config.sections()))
    # root_logger.critical("Auth Key: " + repr(config.get("SECRETS", "auth_key")))

    if request.method == "GET":
        return send_from_directory("./static/html/", "init.html")

    elif request.method == "POST":
        if request.json:
            if request.json["auth"] == config.get("SECRETS", "auth_key"):
                return {
                    "status": "success",
                    "key": str(config.get("SECRETS", "auth_key"))
                    }, status.HTTP_200_OK
            else:
                root_logger.critical("Failed password: " + json.dumps(request.json))
                return {"status": "failed", "error": "Code does not match"}, status.HTTP_401_UNAUTHORIZED

    return 'METHOD NOT ALLOWED', status.HTTP_405_METHOD_NOT_ALLOWED


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(*args, **kwargs):
    flash("NotFound", category="error")
    logging.critical("Flashed!")
    return redirect("/")


@app.before_request
def do_before_request_stuff():
    session.permanent = True

    match request.path:
        case "/":
            access_logger.info(f"{datetime.now().isoformat()} - - {request.remote_addr} accessed the homepage!")
        case "/einstellungen":
            access_logger.warning(f"{datetime.now().isoformat()} - - {request.remote_addr} accessed settings!")

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


@atexit.register
def exit():
    print(bcolors.ENDC)


if __name__ == "__main__":
    app.logger.handlers.clear()
    app.logger.addHandler(werkzeug_handler)

    if args.runProd:

        import waitress
        print(bcolors.OKGREEN + "Production-Ready Server" + bcolors.ENDC)

        print(bcolors.OKBLUE + "Port: ".ljust(10, ".") + " 80" + bcolors.ENDC)
        waitress.serve(app, host="0.0.0.0", port=80)

    elif args.runWaitress:

        import waitress
        print(bcolors.OKCYAN + "Running with waitress" + bcolors.ENDC)
        waitress.serve(app, host="127.0.0.1", port=80)

    elif args.runDebug:
        print(bcolors.WARNING + bcolors.BOLD + "Development server" + bcolors.ENDC)

        app.run(host='127.0.0.1', port=80, debug=True)

    # elif args.runDebug: <-- This does not work, because waitress cannot create an instance if directed from outside
    else:
        app.config['TEMPLATES_AUTO_RELOAD'] = True

        print(bcolors.WARNING + bcolors.BOLD + "Development server" + bcolors.ENDC)

        app.run(host='127.0.0.1', port=80, debug=False)
