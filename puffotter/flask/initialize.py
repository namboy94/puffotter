"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of puffotter.

puffotter is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

puffotter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with puffotter.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import os
import base64
import binascii
import logging
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from typing import List, Optional, Type
from flask import redirect, url_for, flash, render_template
from flask.logging import default_handler
from flask.blueprints import Blueprint
from werkzeug.exceptions import HTTPException
from puffotter.flask.Config import Config
from puffotter.flask.base import app, login_manager, db
from puffotter.flask.enums import AlertSeverity
from puffotter.flask.db.User import User
from puffotter.flask.db.ApiKey import ApiKey
from puffotter.flask.routes.user_management import user_management_blueprint
from puffotter.flask.routes.static import static_blueprint
from puffotter.flask.routes.api.user_management import \
    user_management_api_blueprint


def init_flask(
        module_name: str,
        sentry_dsn: str,
        root_path: str,
        config: Type[Config],
        models: List[Type[db.Model]],
        blueprints: List[Blueprint]
):
    """
    Initializes the flask application
    :param module_name: The name of the module
    :param sentry_dsn: The sentry DSN used for error logging
    :param root_path: The root path of the flask application
    :param config: The Config class to use for configuration
    :param models: The database models to create
    :param blueprints: The routing blueprints to register
    :return: None
    """
    app.root_path = root_path
    try:
        config.load_config(module_name, sentry_dsn)
        missing_variable = None
    except KeyError as e:
        missing_variable = e

    __init_logging(config)
    if missing_variable is not None:
        app.logger.error(f"Missing environment variable: {missing_variable}")
        exit(1)

    for required_template in config.REQUIRED_TEMPLATES.values():
        path = os.path.join(app.root_path, "templates", required_template)
        if not os.path.isfile(path):
            app.logger.error(f"Missing template file {path}")
            exit(1)

    default_blueprints = [
        static_blueprint,
        user_management_blueprint,
        user_management_api_blueprint
    ]
    default_models = [
        User,
        ApiKey
    ]

    __init_app(config, default_blueprints + blueprints)
    __init_db(config, default_models + models)
    __init_login_manager()


def __init_logging(config: Type[Config]):
    """
    Sets up logging to a logfile
    :param config: The configuration to use
    :return: None
    """
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        integrations=[FlaskIntegration()]
    )

    app.logger.removeHandler(default_handler)
    logging.basicConfig(
        filename=config.LOGGING_PATH,
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    app.logger.info("STARTING FLASK")


def __init_app(config: Type[Config], blueprints: List[Blueprint]):
    """
    Initializes the flask app
    :param config: The configuration to use
    :param blueprints: The routing blueprints to register
    :return: None
    """
    app.testing = config.TESTING
    app.config["TRAP_HTTP_EXCEPTIONS"] = True
    app.secret_key = config.FLASK_SECRET
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.context_processor
    def inject_template_variables():
        """
        Injects the project's version string so that it will be available
        in templates
        :return: The dictionary to inject
        """
        return {
            "version": config.VERSION,
            "env": app.env,
            "config": config
        }

    @app.errorhandler(Exception)
    def exception_handling(e: Exception):
        """
        Handles any uncaught exceptions and shows an applicable error page
        :param e: The caught exception
        :return: The response to the exception
        """
        if isinstance(e, HTTPException):
            error = e
            if e.code == 401:
                flash(
                    config.STRINGS["401_message"],
                    AlertSeverity.DANGER.value
                )
                return redirect(url_for("user_management.login"))
        else:
            error = HTTPException(config.STRINGS["500_message"])
            error.code = 500
            app.logger.error("Caught exception: {}".format(e))
        return render_template(
            config.REQUIRED_TEMPLATES["error_page"],
            error=error
        )

    @app.errorhandler(HTTPException)
    def unauthorized_handling(e: HTTPException):
        """
        Forwards HTTP exceptions to the error handler
        :param e: The HTTPException
        :return: The response to the exception
        """
        return exception_handling(e)


def __init_db(config: Type[Config], models: List[db.Model]):
    """
    Initializes the database
    :param config: The configuration to use
    :param models: The models to create in the database
    :return: None
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Makes sure that we don't get errors because
    # of an idle database connection
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)

    for model in models:
        app.logger.debug(f"Loading model {model.__name__}")

    with app.app_context():
        db.create_all()


def __init_login_manager():
    """
    Initializes the login manager
    :return: None
    """
    login_manager.session_protection = "strong"

    # Set up login manager
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """
        Loads a user from an ID
        :param user_id: The ID
        :return: The User
        """
        return User.query.get(int(user_id))

    @login_manager.request_loader
    def load_user_from_request(request) -> Optional[User]:
        """
        Loads a user pased on a provided API key
        :param request: The request containing the API key in the headers
        :return: The user or None if no valid API key was provided
        """
        if "Authorization" not in request.headers:
            return None

        api_key = request.headers["Authorization"].replace("Basic ", "", 1)

        try:
            api_key = base64.b64decode(
                api_key.encode("utf-8")
            ).decode("utf-8")
        except (TypeError, binascii.Error):
            return None

        db_api_key = ApiKey.query.get(api_key.split(":", 1)[0])

        # Check for validity of API key
        if db_api_key is None or not db_api_key.verify_key(api_key):
            return None

        elif db_api_key.has_expired():
            db.session.delete(db_api_key)
            db.session.commit()
            return None

        return User.query.get(db_api_key.user_id)
