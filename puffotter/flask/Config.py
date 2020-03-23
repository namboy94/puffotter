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
import pkg_resources
from typing import Type, Dict, Any, Callable


class Config:
    """
    Class that keeps track of configuration data
    The class attributes should only be called after running load_config
    """

    @classmethod
    def load_config(cls, root_path: str, module_name: str, sentry_dsn: str):
        """
        Loads the configuration from environment variables
        :param root_path: The root path of the application
        :param module_name: The name of the project's module
        :param sentry_dsn: The sentry DSN used for error logging
        :return: None
        """
        try:
            Config.LOGGING_PATH = os.environ.get(
                "LOGGING_PATH",
                os.path.join("/tmp", f"{module_name}.log")
            )
            Config.SENTRY_DSN = sentry_dsn
            Config.VERSION = \
                pkg_resources.get_distribution(module_name).version
            Config.FLASK_SECRET = os.environ["FLASK_SECRET"]
            Config.TESTING = os.environ.get("FLASK_TESTING") == "1"

            if Config.TESTING:
                Config.DB_MODE = "sqlite"
            else:
                Config.DB_MODE = os.environ["DB_MODE"].lower()
            if Config.DB_MODE == "sqlite":
                sqlite_path = os.environ.get(
                    "SQLITE_PATH",
                    os.path.join("/tmp", f"{module_name}.db")
                )
                Config.DB_URI = "sqlite:///" + sqlite_path
            else:
                base = Config.DB_MODE.upper() + "_"
                db_host = os.environ[base + "HOST"]
                db_port = os.environ[base + "PORT"]
                db_user = os.environ[base + "USER"]
                db_password = os.environ[base + "PASSWORD"]
                db_database = os.environ[base + "DATABASE"]
                Config.DB_URI = f"{Config.DB_MODE}://{db_user}:{db_password}@"\
                                f"{db_host}:{db_port}/{db_database}"

            Config.RECAPTCHA_SITE_KEY = os.environ["RECAPTCHA_SITE_KEY"]
            Config.RECAPTCHA_SECRET_KEY = os.environ["RECAPTCHA_SECRET_KEY"]

            Config.SMTP_HOST = os.environ["SMTP_HOST"]
            Config.SMTP_PORT = int(os.environ["SMTP_PORT"])
            Config.SMTP_ADDRESS = os.environ["SMTP_ADDRESS"]
            Config.SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

            cls._load_extras(Config)
        except KeyError as e:
            print(f"Missing environment variable: {e}")
            exit(1)

        for required_template in cls.REQUIRED_TEMPLATES.values():
            path = os.path.join(root_path, "templates", required_template)
            if not os.path.isfile(path):
                print(f"Missing template file {path}")
                exit(1)

    @classmethod
    def _load_extras(cls, parent: Type["Config"]):
        """
        This method can be used to add attributes in subclasses as well as
        change attributes in the base Config class
        :param parent: The base Config class, used to chage attributes
        :return: None
        """
        pass

    VERSION: str
    """
    The current version of the application
    """

    SENTRY_DSN: str
    """
    The sentry DSN used for error logging
    """

    FLASK_SECRET: str
    """
    The flask secret key
    """

    TESTING: bool
    """
    Whether or not testing is enabled
    """

    LOGGING_PATH: str
    """
    The path to the logging file
    """

    FLASK_PORT: int = int(os.environ.get("FLASK_PORT", "8000"))
    """
    The port to use when serving the flask application
    """

    DB_MODE: str
    """
    The database mode (for example 'sqlite' or 'mysql')
    """

    DB_URI: str
    """
    The database URI to use for database operations
    """

    RECAPTCHA_SITE_KEY: str
    """
    Google ReCaptcha site key for bot detection
    """

    RECAPTCHA_SECRET_KEY: str
    """
    Google ReCaptcha secret key for bot detection
    """

    SMTP_HOST: str
    """
    The SMPT Host used for sending emails
    """

    SMTP_PORT: int
    """
    The SMPT Port used for sending emails
    """

    SMTP_ADDRESS: str
    """
    The SMPT Address used for sending emails
    """
    SMTP_PASSWORD: str
    """
    The SMPT Password used for sending emails
    """

    MIN_USERNAME_LENGTH: int = 1
    """
    The Minimum length for usernames
    """

    MAX_USERNAME_LENGTH: int = 12
    """
    The maximum length of usernames
    """

    MAX_API_KEY_AGE: int = 2592000  # 30 days
    """
    The maximum age for API keys
    """

    API_VERSION: str = "1"
    """
    The API Version
    """

    REQUIRED_TEMPLATES: Dict[str, str] = {
        "index": "static/index.html",
        "about": "static/about.html",
        "privacy": "static/privacy.html",
        "error_page": "static/error_page.html",
        "registration_email": "email/registration.html",
        "forgot_password_email": "email/forgot_password.html",
        "forgot": "user_management/forgot.html",
        "login": "user_management/login.html",
        "profile": "user_management/profile.html",
        "register": "user_management/register.html"
    }
    """
    Specifies required template files
    """

    STRINGS: Dict[str, str] = {
        "401_message": "You are not logged in",
        "500_message": "The server encountered an internal error and "
                       "was unable to complete your request. "
                       "Either the server is overloaded or there "
                       "is an error in the application.",
        "user_does_not_exist": "User does not exist",
        "user_already_logged_in": "User already logged in",
        "user_already_confirmed": "User already confirmed",
        "user_is_not_confirmed": "User is not confirmed",
        "invalid_password": "Invalid Password",
        "logged_in": "Logged in successfully",
        "logged_out": "Logged out",
        "username_length": "Username must be between {} and {} characters "
                           "long",
        "passwords_do_not_match": "Passwords do not match",
        "email_already_in_use": "Email already in use",
        "username_already_exists": "Username already exists",
        "recaptcha_incorrect": "ReCaptcha not solved correctly",
        "registration_successful": "Registered Successfully. Check your email "
                                   "inbox for confirmation",
        "registration_email_title": "Registration",
        "confirmation_key_invalid": "Confirmation key invalid",
        "user_confirmed_successfully": "User confirmed successfully",
        "password_reset_email_title": "Password Reset",
        "password_was_reset": "Password was reset successfully",
        "password_changed": "Password changed successfully",
        "user_was_deleted": "User was deleted"
    }
    """
    Dictionary that defines various strings used in the application.
    Makes it easier to use custom phrases.
    """

    TEMPLATE_EXTRAS: Dict[str, Callable[[], Dict[str, Any]]] = {
        "index": lambda: {},
        "about": lambda: {},
        "privacy": lambda: {},
        "login": lambda: {},
        "register": lambda: {},
        "forgot": lambda: {},
        "profile": lambda: {},
        "registration_email": lambda: {},
        "forgot_email": lambda: {}
    }
    """
    This can be used to provide the template rendering engine additional
    parameters, which may be necessary when adding UI elements.
    This is done with functions that don't expect any input and
    return a dictionary of keys and values to be passed to the template
    rendering engine
    """
