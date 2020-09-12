"""LICENSE
Copyright 2017 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bundesliga-tippspiel.

bundesliga-tippspiel is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

bundesliga-tippspiel is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with bundesliga-tippspiel.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

# noinspection PyProtectedMember
from unittest import TestCase
from puffotter.units import human_readable_bytes


class TestUnits(TestCase):
    """
    Tests cryptographical functions
    """

    def test_converting_bytes_to_human_readable(self):
        """
        Tests that bytes are successfully converted to human readable format.
        :return: None
        """
        self.assertEqual("1MB", human_readable_bytes(1000000))
        self.assertEqual("1.024KB", human_readable_bytes(1024))
        self.assertEqual("0.123KB", human_readable_bytes(123))
        self.assertEqual("1.234GB", human_readable_bytes(1234123123))
