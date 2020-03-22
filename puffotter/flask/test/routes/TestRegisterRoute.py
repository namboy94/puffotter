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

from unittest.mock import patch
from puffotter.flask.test.TestFramework import _TestFramework
from puffotter.flask.db.User import User
from puffotter.flask.Config import Config


class TestRegisterRoute(_TestFramework):
    """
    Class that tests registration features
    """

    def test_page_get(self):
        """
        Tests getting the page
        :return: None
        """
        resp = self.client.get("/register")
        self.assertTrue(b"<!--user_management/register.html-->" in resp.data)

    def test_registering_user(self):
        """
        Tests registering a new user
        :return: None
        """
        self.assertEqual(len(User.query.all()), 0)
        with self.client:

            with patch("puffotter.flask.routes.user_management.send_email") \
                    as m:
                self.assertEqual(0, m.call_count)
                resp = self.client.post(
                    "/register",
                    follow_redirects=True,
                    data={
                        "username": "testuser",
                        "password": "testpass",
                        "password-repeat": "testpass",
                        "email": "test@example.com",
                        "g-recaptcha-response": ""
                    }
                )
                self.assertEqual(1, m.call_count)

            registration = self.config.STRINGS["registration_successful"]
            self.assertTrue(registration.encode("utf-8") in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertEqual(len(User.query.all()), 1)

            user = User.query.filter_by(username="testuser").first()
            self.assertEqual(user.email, "test@example.com")
            self.assertFalse(user.confirmed)

    def test_invalid_registrations(self):
        """
        Tests registering using invalid parameters
        :return: None
        """
        user, _, _ = self.generate_sample_user()
        base = {
            "username": "testuser",
            "password": "testpass",
            "password-repeat": "testpass",
            "email": "test@example.com",
            "g-recaptcha-response": ""
        }
        self.assertEqual(len(User.query.all()), 1)
        with self.client:

            for params in [
                {"password": "testpasses",
                 "expected": "passwords_do_not_match"},
                {"username": "-" * (Config.MIN_USERNAME_LENGTH - 1),
                 "expected": "username_length"},
                {"username": "-" * (Config.MAX_USERNAME_LENGTH + 1),
                 "expected": "username_length"},
                {"username": user.username,
                 "expected": "username_already_exists"},
                {"email": user.email,
                 "expected": "email_already_in_use"}
            ]:
                data = dict(base)
                data.update(params)

                with patch("puffotter.flask.routes.user_management."
                           "send_email")as m:
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/register",
                        follow_redirects=True,
                        data=data
                    )
                    self.assertEqual(0, m.call_count)

                expected = self.config.STRINGS[params["expected"]]
                if params["expected"] == "username_length":
                    expected = expected[0:20]

                registration = self.config.STRINGS["registration_successful"]
                self.assertFalse(registration.encode("utf-8") in resp.data)
                self.assertTrue(
                    b"<!--user_management/register.html-->" in resp.data
                )
                self.assertTrue(expected.encode("utf-8") in resp.data)
                self.assertEqual(len(User.query.all()), 1)

    def test_invalid_recaptcha(self):
        """
        Tests that invalid ReCaptcha responses are handled correctly
        :return: None
        """
        with self.client:
            with patch("puffotter.flask.routes.user_management.send_email") \
                    as m:
                with patch("puffotter.flask.routes.user_management."
                           "verify_recaptcha", lambda x, y, z: False):
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/register",
                        follow_redirects=True,
                        data={
                            "username": "testuser",
                            "password": "testpass",
                            "password-repeat": "testpass",
                            "email": "test@example.com",
                            "g-recaptcha-response": ""
                        }
                    )
                    self.assertEqual(0, m.call_count)

            registration = self.config.STRINGS["registration_successful"]
            recaptcha = self.config.STRINGS["recaptcha_incorrect"]
            self.assertFalse(registration.encode("utf-8") in resp.data)
            self.assertTrue(recaptcha.encode("utf-8") in resp.data)
            self.assertTrue(
                b"<!--user_management/register.html-->" in resp.data
            )
            self.assertEqual(len(User.query.all()), 0)

    def test_confirming(self):
        """
        Tests confirming a user
        :return: None
        """
        user, _, confirm_key = self.generate_sample_user(False)
        with self.client:
            resp = self.client.get("/confirm?user_id={}&confirm_key={}".format(
                user.id, confirm_key
            ), follow_redirects=True)
            confirmed = self.config.STRINGS["user_confirmed_successfully"]
            self.assertTrue(confirmed.encode("utf-8") in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertTrue(user.confirmed)

    def test_invalid_confirm(self):
        """
        Tests invalid confirmations
        :return: None
        """
        user, _, confirm_key = self.generate_sample_user(False)
        user2, _, confirm_key2 = self.generate_sample_user()
        with self.client:
            for params in [
                {"user_id": "100", "confirm_key": confirm_key,
                 "expected": "user_does_not_exist"},
                {"user_id": user.id, "confirm_key": "AAA",
                 "expected": "confirmation_key_invalid"},
                {"user_id": user2.id, "confirm_key": confirm_key2,
                 "expected": "user_already_confirmed"}
            ]:
                resp = self.client.get(
                    "/confirm?user_id={}&confirm_key={}".format(
                        params["user_id"], params["confirm_key"]
                    ), follow_redirects=True)
                expected = self.config.STRINGS[params["expected"]]
                confirmed = self.config.STRINGS["user_confirmed_successfully"]

                self.assertFalse(confirmed.encode("utf-8") in resp.data)
                self.assertTrue(b"<!--static/index.html-->" in resp.data)
                self.assertTrue(expected.encode("utf-8") in resp.data)
                self.assertFalse(user.confirmed)
