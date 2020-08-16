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
import shutil
from base64 import b64encode
from unittest import TestCase
from typing import Tuple, Dict, List, Type, Callable
from flask.blueprints import Blueprint
from flask_login import login_user
from puffotter.crypto import generate_random, generate_hash
from puffotter.flask.Config import Config
from puffotter.flask.db.User import User
from puffotter.flask.db.ApiKey import ApiKey
from puffotter.flask.initialize import init_flask, app, db
from puffotter.env import load_env_file


class _TestFramework(TestCase):
    """
    Class that models a testing framework for the flask application
    """

    GENERATED_USER_CREDENTIALS: List[Tuple[str, str, str, str]] = []
    """
    List of dynamically generated generated user credentials
    (password, password hash, confirmation key, confirmation hash)
    Used to increase speed of the tests, since hashing with bcrypt takes a
    relatively long time
    """

    GENERATED_API_KEY_CREDENTIALS: List[Tuple[str, str]] = []
    """
    List of dynamically generated API keys and their hashes.
    Used to speed up the testing
    """

    module_name: str = "puffotter"
    models: List[db.Model] = []
    blueprint_generators: List[Tuple[Callable[[str], Blueprint], str]] = []
    root_path: str = "."
    config: Type[Config] = Config

    def setUp(self):
        """
        Sets up the flask application and a temporary database to test with
        :return: None
        """
        self.user_cred_count = 0
        self.api_cred_count = 0

        self.temp_templates_dir = "templates"
        self.templates_sample_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates"
        )
        os.environ["FLASK_TESTING"] = "1"
        os.environ["DB_MODE"] = "sqlite"
        os.environ["FLASK_SECRET"] = generate_random(20)

        self.cleanup(True)
        if self.module_name == "puffotter":
            shutil.copytree(self.templates_sample_dir, self.temp_templates_dir)
            os.environ["RECAPTCHA_SITE_KEY"] = ""
            os.environ["RECAPTCHA_SECRET_KEY"] = ""
            os.environ["SMTP_HOST"] = ""
            os.environ["SMTP_PORT"] = "0"
            os.environ["SMTP_ADDRESS"] = ""
            os.environ["SMTP_PASSWORD"] = ""
            os.environ["TELEGRAM_API_KEY"] = ""
        else:
            load_env_file()

        self.config.load_config(self.root_path, self.module_name, "")
        self.db_path = Config.DB_URI.split("sqlite:///")[1]
        self.cleanup(False)

        self.app = app
        self.db = db

        init_flask(
            self.module_name,
            "",
            self.root_path,
            self.config,
            self.models,
            self.blueprint_generators
        )
        self.app.app_context().push()

        self.client = self.app.test_client()
        self.context = self.app.test_request_context()

    def tearDown(self):
        """
        Removes any generated files from the filesystem and handles other
        post-test tasks
        :return: None
        """
        self.cleanup(True)

    def cleanup(self, remove_templates: bool = True):
        """
        Cleans up the filesystem after/before tests
        :return: None
        """
        try:
            if self.db_path != "" and os.path.isfile(self.db_path):
                os.remove(self.db_path)
        except AttributeError:
            pass
        if os.path.isdir(self.temp_templates_dir) and remove_templates:
            shutil.rmtree(self.temp_templates_dir)

    def generate_sample_user(self, confirmed: bool = True) \
            -> Tuple[User, str, str]:
        """
        Generates a random user for use in tests
        :param confirmed: Whether or not the user should be confirmed
        :return: The User object, the password and the confirmation key
        """
        if self.user_cred_count >= \
                len(_TestFramework.GENERATED_USER_CREDENTIALS):
            password = generate_random(20)
            password_hash = generate_hash(password)
            confirm_key = generate_random(20)
            confirmation_hash = generate_hash(confirm_key)
            _TestFramework.GENERATED_USER_CREDENTIALS.append(
                (password, password_hash, confirm_key, confirmation_hash)
            )
        else:
            password, password_hash, confirm_key, confirmation_hash = \
                _TestFramework.GENERATED_USER_CREDENTIALS[self.user_cred_count]
        self.user_cred_count += 1

        user = User(
            username=generate_random(12),
            password_hash=password_hash,
            email=generate_random(8) + "@example.com",
            confirmed=confirmed,
            confirmation_hash=confirmation_hash
        )
        self.db.session.add(user)
        self.db.session.commit()
        return user, password, confirm_key

    def login_user(self, user: User, password: str, use_client: bool = True):
        """
        Logs in a user
        :param user: The user to log in
        :param password: The password to use
        :param use_client: Whether or not to use the testing clienty
        :return: None
        """
        if use_client:
            self.client.post("/login", follow_redirects=True, data={
                "username": user.username,
                "password": password
            })
        else:
            applicable_hashes = [
                x[1]
                for x in _TestFramework.GENERATED_USER_CREDENTIALS
                if x[0] == password
            ]
            if user.password_hash not in applicable_hashes:
                return
            else:
                with self.context:
                    login_user(user)

    def generate_api_key(self, user: User) \
            -> Tuple[ApiKey, str, Dict[str, str]]:
        """
        Generates an API key and base64 encoded headers for requests
        :param user: The user for which to create the key
        :return: The API key object, the actual API key, the headers
        """
        if self.api_cred_count >= \
                len(_TestFramework.GENERATED_API_KEY_CREDENTIALS):
            key = generate_random(20)
            hashed = generate_hash(key)
            _TestFramework.GENERATED_API_KEY_CREDENTIALS.append((key, hashed))
        else:
            key, hashed = _TestFramework.GENERATED_API_KEY_CREDENTIALS[
                self.api_cred_count
            ]
        self.api_cred_count += 1

        api_key_obj = ApiKey(user=user, key_hash=hashed)
        self.db.session.add(api_key_obj)
        self.db.session.commit()
        api_key = "{}:{}".format(api_key_obj.id, key)

        return api_key_obj, api_key, self.generate_api_key_headers(api_key)

    # noinspection PyMethodMayBeStatic
    def generate_api_key_headers(self, api_key: str) -> Dict[str, str]:
        """
        Creates HTTP Authorization headers for an API key
        :param api_key: The API key to put in the headers
        :return: The headers
        """
        encoded = b64encode(api_key.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": "Basic {}".format(encoded)
        }
