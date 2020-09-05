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

from enum import Enum
from typing import Dict, Any
from puffotter.flask.base import db
from puffotter.flask.db.ModelMixin import ModelMixin
from puffotter.flask.test.TestFramework import _TestFramework


class TestModelMixin(_TestFramework):
    """
    Class that tests the ModelMixin class
    """

    def test_enum_attributes(self):
        """
        Tests if the repr method handles enums correctly
        :return: None
        """

        class A(Enum):
            B = 1
            C = 2

        class Tester(ModelMixin, db.Model):
            enum = db.Column(db.Enum(A))

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def __json__(self, include_children: bool = False,  _=None) \
                    -> Dict[str, Any]:
                return {"id": self.id, "enum": self.enum.value}

        tester = Tester(id=1, enum=A.B)
        self.assertEqual(repr(tester), "Tester(id=1, enum=A.B)")
