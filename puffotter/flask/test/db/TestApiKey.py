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

import time
from puffotter.flask.Config import Config
from puffotter.flask.db.ApiKey import ApiKey
from puffotter.flask.test.TestFramework import _TestFramework


class TestApiKey(_TestFramework):
    """
    Class that tests the ApiKey database model
    """

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key = self.generate_api_key(user)[0]
        self.assertEqual(
            api_key.__json__(False),
            {
                "id": api_key.id,
                "user_id": user.id,
                "creation_time": api_key.creation_time
            }
        )
        self.assertEqual(
            api_key.__json__(True),
            {
                "id": api_key.id,
                "user_id": user.id,
                "user": user.__json__(True),
                "creation_time": api_key.creation_time
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key = self.generate_api_key(user)[0]
        data = api_key.__json__()
        data.pop("id")
        self.assertEqual(
            str(api_key),
            "ApiKey:{} <{}>".format(api_key.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key = self.generate_api_key(user)[0]
        generated = {"value": api_key}
        code = repr(api_key)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], api_key)
        self.assertFalse(generated["value"] is api_key)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key = self.generate_api_key(user)[0]
        api_key2 = self.generate_api_key(user)[0]
        mapping = {
            api_key: 100,
            api_key2: 200
        }
        self.assertEqual(mapping[api_key], 100)
        self.assertEqual(mapping[api_key2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key = self.generate_api_key(user)[0]
        api_key2 = self.generate_api_key(user)[0]
        self.assertEqual(api_key, api_key)
        self.assertNotEqual(api_key, api_key2)
        self.assertNotEqual(api_key, 100)

    def test_verifying_key(self):
        """
        Tests verifying an api key
        :return: None
        """
        user = self.generate_sample_user()[0]
        api_key, key, _ = self.generate_api_key(user)
        self.assertTrue(api_key.verify_key(key))
        self.assertFalse(api_key.verify_key("A:1"))
        self.assertFalse(api_key.verify_key("100:" + key.split(":", 1)[1]))
        self.assertFalse(api_key.verify_key("{}:ABC".format(api_key.id)))

    def test_expiration(self):
        """
        Tests if the expiration of API keys works correctly
        :return: None
        """
        self.assertTrue(ApiKey(creation_time=0).has_expired())
        self.assertTrue(ApiKey(
            creation_time=time.time() - Config.MAX_API_KEY_AGE
        ).has_expired())
        self.assertFalse(ApiKey(
            creation_time=time.time() - Config.MAX_API_KEY_AGE + 1
        ).has_expired())
        self.assertFalse(ApiKey(creation_time=time.time()).has_expired())
        backup = Config.MAX_API_KEY_AGE
        Config.MAX_API_KEY_AGE = 0
        self.assertTrue(ApiKey(creation_time=time.time()).has_expired())
        Config.MAX_API_KEY_AGE = backup
