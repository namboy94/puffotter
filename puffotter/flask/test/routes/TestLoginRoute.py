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

from flask_login import current_user
from puffotter.flask.test.TestFramework import _TestFramework


class TestLoginRoute(_TestFramework):
    """
    Class that tests log-in features
    """

    def test_page_get(self):
        """
        Tests getting the page
        :return: None
        """
        resp = self.client.get("/login")
        self.assertTrue(b"<!--user_management/login.html-->" in resp.data)

    def test_logging_in_and_out(self):
        """
        Tests logging in successfully, then once more, then logging out
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            self.assertFalse(bool(current_user))
            resp = self.client.post("/login", follow_redirects=True, data={
                "username": user.username,
                "password": password
            })
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertTrue(b"Logged in successfully" in resp.data)
            self.assertTrue(current_user.is_authenticated)

            resp = self.client.get("/profile")
            self.assertTrue(user.username.encode("utf-8") in resp.data)

            resp = self.client.post("/login", follow_redirects=True, data={
                "username": user.username,
                "password": password
            })

            logged_in = self.config.STRINGS["logged_in"]
            already_logged_in = self.config.STRINGS["user_already_logged_in"]
            logged_out = self.config.STRINGS["logged_out"]

            self.assertFalse(logged_in.encode("utf-8") in resp.data)
            self.assertTrue(already_logged_in.encode("utf-8") in resp.data)
            self.assertTrue(b"<!--user_management/login.html-->" in resp.data)
            self.assertTrue(current_user.is_authenticated)

            resp = self.client.get("/logout", follow_redirects=True)
            self.assertFalse(current_user.is_authenticated)
            self.assertTrue(logged_out.encode("utf-8") in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)

    def test_invalid_login_attempts(self):
        """
        Tests trying to log in with invalid credentials etc
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        user2, password2, _ = self.generate_sample_user(confirmed=False)
        with self.client:
            for params in [
                {
                    "username": user.username,
                    "password": password + "AAA",
                    "expected": "invalid_password"
                },
                {
                    "username": user.username + "AAA",
                    "password": password,
                    "expected": "user_does_not_exist"
                },
                {
                    "username": user2.username,
                    "password": password2,
                    "expected": "user_is_not_confirmed"
                }
            ]:
                resp = self.client.post(
                    "/login", follow_redirects=True, data=params
                )
                logged_in = self.config.STRINGS["logged_in"]
                expected = self.config.STRINGS[params["expected"]]
                print(expected)
                print(resp.data)

                self.assertFalse(logged_in.encode("utf-8") in resp.data)
                self.assertTrue(expected.encode("utf-8") in resp.data)
                self.assertTrue(
                    b"<!--user_management/login.html-->" in resp.data
                )
                self.assertFalse(current_user.is_authenticated)

                resp = self.client.get("/profile")
                self.assertFalse(user.username.encode("utf-8") in resp.data)
