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
from typing import Type, Dict, Any, Callable, List, Optional
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.settings.impl.TelegramBotSettings import TelegramBotSettings
from bokkichat.connection.impl.TelegramBotConnection import \
    TelegramBotConnection


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
        cls.ensure_environment_variables_present()

        Config.LOGGING_PATH = os.environ.get(
            "LOGGING_PATH",
            os.path.join("/tmp", f"{module_name}.log")
        )
        Config.DEBUG_LOGGING_PATH = os.environ.get(
            "DEBUG_LOGGING_PATH",
            os.path.join("/tmp", f"{module_name}-debug.log")
        )
        Config.SENTRY_DSN = sentry_dsn
        Config.VERSION = \
            pkg_resources.get_distribution(module_name).version
        Config.FLASK_SECRET = os.environ["FLASK_SECRET"]
        Config.TESTING = os.environ.get("FLASK_TESTING") == "1"
        Config.BEHIND_PROXY = os.environ.get("BEHIND_PROXY") == "1"

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
        Config.TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

        cls._load_extras(Config)

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

    @classmethod
    def environment_variables(cls) -> Dict[str, List[str]]:
        """
        Specifies required and optional environment variables
        :return: The specified environment variables in two lists in
                 a dictionary, grouped by whether the variables are
                 required or optional
        """
        required = [
            "FLASK_SECRET",
            "DB_MODE",
            "RECAPTCHA_SITE_KEY",
            "RECAPTCHA_SECRET_KEY",
            "SMTP_HOST",
            "SMTP_PORT",
            "SMTP_ADDRESS",
            "SMTP_PASSWORD",
            "TELEGRAM_API_KEY"
        ]
        optional = [
            "LOGGING_PATH",
            "DEBUG_LOGGING_PATH",
            "FLASK_TESTING",
            "DOMAIN_NAME",
            "HTTP_PORT",
            "BEHIND_PROXY"
        ]

        db_mode = os.environ.get("DB_MODE")
        if db_mode == "sqlite":
            optional.append("SQLITE_PATH")
        elif db_mode is not None:
            db_mode = db_mode.upper()
            required.append(f"{db_mode}_HOST")
            required.append(f"{db_mode}_PORT")
            required.append(f"{db_mode}_USER")
            required.append(f"{db_mode}_PASSWORD")
            required.append(f"{db_mode}_DATABASE")

        return {
            "required": required,
            "optional": optional
        }

    @classmethod
    def ensure_environment_variables_present(cls):
        """
        Makes sure that all required environment variables have been set.
        If this is not the case, the app will exit.
        :return: None
        """
        for env_name in cls.environment_variables()["required"]:
            if env_name not in os.environ:
                print(f"Missing environment variable: {env_name}")
                exit(1)

    @classmethod
    def dump_env_variables(cls, path: Optional[str] = None):
        """
        Dumps all environment variables used by this application to a file
        :param path: The path to the file to which to dump the content.
                     If this is None, the file contents will be printed.
        :return: None
        """
        envs = ""
        all_env_names = cls.environment_variables()["required"] + \
            cls.environment_variables()["optional"]
        for env_name in all_env_names:
            value = os.environ.get(env_name)
            if value is not None:
                envs += f"{env_name}={value}\n"

        if path is not None:
            with open(path, "w") as f:
                f.write(envs)
        else:
            print(envs)

    @classmethod
    def base_url(cls) -> str:
        """
        :return: The base URL of the website
        """
        if cls.BEHIND_PROXY:
            return f"https://{cls.DOMAIN_NAME}"
        else:
            return f"http://{cls.DOMAIN_NAME}:{cls.HTTP_PORT}"

    @classmethod
    def initialize_telegram(cls):
        """
        Initializes the telegram bot connection
        :return: None
        """
        Config.TELEGRAM_BOT_CONNECTION = TelegramBotConnection(
            TelegramBotSettings(Config.TELEGRAM_API_KEY)
        )

    @classmethod
    def telegram_bg(cls):
        """
        Specifies the background behaviour of the telegram bot
        By default, the bot listens to /whoami messages
        and answers with the telegram chat ID
        :return: None
        """
        telegram = cls.TELEGRAM_BOT_CONNECTION

        def handler(_, msg):
            if msg.is_text():
                msg: TextMessage = msg
                print(msg.body)

                if msg.body == "/whoami":
                    sender = telegram.address
                    receiver = msg.sender
                    telegram.send(
                        TextMessage(sender, receiver, receiver.address))

        telegram.loop(handler)

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

    DEBUG_LOGGING_PATH: str
    """
    The path to the debug logging path
    """

    WARNING_LOGGING_PATH: str
    """
    The path to the logging path for WARNING messages
    """

    HTTP_PORT: int = int(os.environ.get("HTTP_PORT", "80"))
    """
    The port to use when serving the flask application
    """

    DOMAIN_NAME: str = os.environ.get("DOMAIN_NAME", "localhost")
    """
    The domain name of the website
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

    TELEGRAM_API_KEY: str
    """
    API key for a telegram bot
    """

    TELEGRAM_BOT_CONNECTION: TelegramBotConnection
    """
    Telegram bot connection
    """

    BEHIND_PROXY: bool
    """
    Whether or not the site is being served by a reverse proxy like nginx.
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
        "user_was_deleted": "User was deleted",
        "telegram_chat_id_set": "Telegram Chat ID was set"
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
