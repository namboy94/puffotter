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
from unittest.mock import patch
from puffotter.flask.test.TestFramework import _TestFramework
from puffotter.flask.wsgi import start_server, \
    __start_background_tasks as start_background_tasks


class TestWsgi(_TestFramework):
    """
    Tests the WSGI server
    """

    def test_starting_and_stopping_wsgi_server(self):
        """
        Tests starting and stopping the WSGI server
        :return: None
        """
        class Server:
            def __init__(self, *arg, **kwargs):
                pass

            def start(self):
                raise KeyboardInterrupt()

            def stop(self):
                pass

        with patch("puffotter.flask.wsgi.Server", Server):
            start_server(self.config, {})

    def test_starting_background_tasks(self):
        """
        Tests starting background tasks
        :return: None
        """
        self.config.START = time.time()

        def test_task():
            delta = time.time() - self.config.START
            if 1 < delta < 2:
                raise ValueError("TestException")
            elif delta >= 2:
                exit(0)

        tasks = {
            "test_task": (1, test_task)
        }
        start_background_tasks(tasks)
