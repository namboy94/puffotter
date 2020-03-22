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

from puffotter.flask.test.TestFramework import _TestFramework
from puffotter.flask.db.User import User


class TestProfileRoute(_TestFramework):
    """
    Class that tests profile features
    """

    def test_page_get(self):
        """
        Tests getting the page
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            self.login_user(user, password)
            resp = self.client.get("/profile")
            self.assertTrue(
                b"<!--user_management/profile.html-->" in resp.data
            )
            self.assertTrue(user.username.encode("utf-8") in resp.data)

    def test_changing_password(self):
        """
        Tests changing a password
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        new_pass = "abcdefg"
        with self.client:
            self.login_user(user, password)
            resp = self.client.post("/change_password", follow_redirects=True,
                                    data={
                                        "old_password": password,
                                        "new_password": new_pass,
                                        "password_repeat": new_pass
                                    })
            self.assertTrue(
                b"<!--user_management/profile.html-->" in resp.data
            )
            password_changed = self.config.STRINGS["password_changed"]
            self.assertTrue(password_changed.encode("utf-8") in resp.data)
            self.assertFalse(user.verify_password(password))
            self.assertTrue(user.verify_password(new_pass))

    def test_unsuccessful_password_change(self):
        """
        Tests unsuccessfully changing a password
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        new_pass = "abcdefg"
        base = {
            "old_password": password,
            "new_password": new_pass,
            "password_repeat": new_pass
        }
        with self.client:
            self.login_user(user, password)
            for params in [
                {"new_password": "AAA", "expected": "passwords_do_not_match"},
                {"old_password": "AAA", "expected": "invalid_password"}
            ]:
                data = dict(base)
                data.update(params)

                resp = self.client.post(
                    "/change_password", follow_redirects=True, data=data
                )
                self.assertTrue(
                    b"<!--user_management/profile.html-->" in resp.data
                )
                expected = self.config.STRINGS[params["expected"]]
                password_changed = self.config.STRINGS["password_changed"]
                self.assertTrue(expected.encode("utf-8") in resp.data)
                self.assertFalse(password_changed.encode("utf-8") in resp.data)
                self.assertTrue(user.verify_password(password))
                self.assertFalse(user.verify_password(new_pass))

    def test_user_delete(self):
        """
        Tests deleting a user
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            self.login_user(user, password)
            self.assertEqual(len(User.query.all()), 1)

            resp = self.client.post("/delete_user", follow_redirects=True,
                                    data={"password": password})
            user_deleted = self.config.STRINGS["user_was_deleted"]

            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertTrue(user_deleted.encode("utf-8") in resp.data)
            self.assertEqual(len(User.query.all()), 0)

    def test_unsuccessful_user_delete(self):
        """
        Tests unsuccessfully deleting a user
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            self.login_user(user, password)
            self.assertEqual(len(User.query.all()), 1)
            resp = self.client.post("/delete_user", follow_redirects=True,
                                    data={"password": "AAA"})
            self.assertTrue(
                b"<!--user_management/profile.html-->" in resp.data
            )
            invalid_password = self.config.STRINGS["invalid_password"]
            self.assertTrue(invalid_password.encode("utf-8") in resp.data)
            self.assertEqual(len(User.query.all()), 1)
