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

from flask.blueprints import Blueprint
from typing import List, Tuple, Callable
from puffotter.flask.routes.static import define_blueprint as __static
from puffotter.flask.routes.user_management import define_blueprint \
    as __user_management
from puffotter.flask.routes.api.user_management import define_blueprint \
    as __api_user_management

blueprint_generators: List[Tuple[Callable[[str], Blueprint], str]] = [
    (__static, "static"),
    (__user_management, "user_management"),
    (__api_user_management, "api_user_management")
]
"""
Defines the functions used to create the various blueprints
as well as their names
"""
