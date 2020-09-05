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

from puffotter.flask.db.TelegramChatId import TelegramChatId
from puffotter.flask.test.TestFramework import _TestFramework


class TestUser(_TestFramework):
    """
    Class that tests the User database model
    """

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        should = {
            "id": user.id,
            "email": user.email,
            "confirmed": True,
            "username": user.username
        }
        self.assertEqual(user.__json__(False), should)
        should.update({
            "telegram_chat_id": None,
            "api_keys": []
        })
        self.assertEqual(user.__json__(True), should)

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        data = user.__json__()
        data.pop("id")
        self.assertEqual(
            str(user),
            "User:{} <{}>".format(user.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        user = self.generate_sample_user()[0]
        generated = {"value": user}
        code = repr(user)

        # noinspection PyUnresolvedReferences
        from puffotter.flask.db.User import User

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], user)
        self.assertFalse(generated["value"] is user)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        user = self.generate_sample_user()[0]
        user2 = self.generate_sample_user()[0]
        mapping = {
            user: 100,
            user2: 200
        }
        self.assertEqual(mapping[user], 100)
        self.assertEqual(mapping[user2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        user = self.generate_sample_user()[0]
        user2 = self.generate_sample_user()[0]
        self.assertEqual(user, user)
        self.assertNotEqual(user, user2)
        self.assertNotEqual(user, 100)

    def test_flask_properties(self):
        """
        Tests if the flask_login properties work as expected
        :return: None
        """
        user = self.generate_sample_user()[0]
        self.assertEqual(user.is_authenticated, True)
        self.assertEqual(user.is_anonymous, False)
        self.assertEqual(user.is_active, user.confirmed)
        self.assertEqual(user.get_id(), str(user.id))

    def test_verifying_password(self):
        """
        Tests verifying the password of a user
        :return: None
        """
        user, password, confirm_key = self.generate_sample_user()
        self.assertTrue(user.verify_password(password))
        self.assertFalse(user.verify_password("AAAAAA"))
        self.assertTrue(user.verify_confirmation(confirm_key))
        self.assertFalse(user.verify_confirmation("AAAAAA"))

    def test_json_with_telegram_chat_id(self):
        """
        Tests whether or not including children can cause recursion errors
        :return: None
        """
        user, _, _ = self.generate_sample_user(True)
        chat_id = TelegramChatId(user=user, chat_id="AAA")
        api_key, _, _ = self.generate_api_key(user)
        self.db.session.add(chat_id)
        self.db.session.commit()
        should = user.__json__(False)
        should.update({
            "telegram_chat_id": chat_id.__json__(True),
            "api_keys": [api_key.__json__(True)]
        })
        should["telegram_chat_id"].pop("user")
        for x in should["api_keys"]:
            x.pop("user")
        self.assertEqual(user.__json__(True), should)
