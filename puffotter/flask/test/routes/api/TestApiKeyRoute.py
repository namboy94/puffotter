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

import json
from puffotter.flask.test.TestFramework import _TestFramework
from puffotter.flask.db.ApiKey import ApiKey


class TestApiKeyRoute(_TestFramework):
    """
    Class that tests API-key related features
    """

    def test_requesting_api_key(self):
        """
        Tests requesting an API key
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        self.assertEqual(len(ApiKey.query.all()), 0)
        resp = self.client.post("/api/v1/key", json={
            "username": user.username,
            "password": password
        })
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))

        self.assertEqual(len(ApiKey.query.all()), 1)
        self.assertEqual(data["status"], "ok")

        api_key = data["data"]["api_key"]
        api_key_obj = ApiKey.query.filter_by(user=user).first()
        api_headers = self.generate_api_key_headers(api_key)

        self.assertTrue(api_key_obj.verify_key(api_key))

        resp = self.client.get(
            "/api/v1/authorize", headers=api_headers, json={}
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))
        self.assertEqual(data["status"], "ok")

    def test_requesting_invalid_api_keys(self):
        """
        Tests requesting API keys with invalid data
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        user2, password2, _ = self.generate_sample_user(False)
        base = {
            "username": user.username,
            "password": password
        }
        for args in [
            {"username": "ABC", "expected": "user does not exist"},
            {"password": "ABC", "expected": "password is incorrect"},
            {"username": user2.username, "password": password2,
             "expected": "user is not confirmed"}
        ]:
            self.assertEqual(len(ApiKey.query.all()), 0)
            params = dict(base)
            params.update(args)
            resp = self.client.post("/api/v1/key", json=params)
            self.assertEqual(resp.status_code, 401)
            data = json.loads(resp.data.decode("utf-8"))
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["reason"], args["expected"])
            self.assertEqual(len(ApiKey.query.all()), 0)

    def test_revoking_api_key(self):
        """
        Tests revoking an API key
        :return: None
        """
        user, _, _ = self.generate_sample_user()
        _, api_key, _ = self.generate_api_key(user)

        self.assertEqual(len(ApiKey.query.all()), 1)

        resp = self.client.delete("/api/v1/key", json={"api_key": api_key})
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data.decode("utf-8"))
        self.assertEqual(data["status"], "ok")

        self.assertEqual(len(ApiKey.query.all()), 0)

    def test_unsuccessfully_revoking_api_key(self):
        """
        Tests unsuccessfully revoking an API key
        :return: None
        """
        user, _, _ = self.generate_sample_user()
        api_key_obj, api_key, _ = self.generate_api_key(user)

        for params in [
            {"api_key": "ABC", "expected": "api key does not exist"},
            {"api_key": "{}:ABC".format(api_key_obj.id),
             "expected": "api key not valid"}
        ]:
            self.assertEqual(len(ApiKey.query.all()), 1)

            resp = self.client.delete("/api/v1/key", json=params)
            self.assertEqual(resp.status_code, 401)
            data = json.loads(resp.data.decode("utf-8"))
            self.assertEqual(data["status"], "error")
            self.assertEqual(data["reason"], params["expected"])

            self.assertEqual(len(ApiKey.query.all()), 1)
