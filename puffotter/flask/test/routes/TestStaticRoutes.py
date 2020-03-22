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


class TestStaticRoutes(_TestFramework):
    """
    Class that tests static pages
    """

    def test_get_index(self):
        """
        Tests getting the index page
        :return: None
        """
        resp = self.client.get("/")
        self.assertTrue(b"<!--static/index.html-->" in resp.data)

    def test_get_about(self):
        """
        Tests getting the about page
        :return: None
        """
        resp = self.client.get("/about")
        self.assertTrue(b"<!--static/about.html-->" in resp.data)

    def test_get_privacy(self):
        """
        Tests getting the privacy page
        :return: None
        """
        resp = self.client.get("/privacy")
        self.assertTrue(b"<!--static/privacy.html-->" in resp.data)
