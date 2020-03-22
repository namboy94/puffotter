"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of fat-ffipd.

fat-ffipd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

fat-ffipd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fat-ffipd.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import Union
from flask import render_template, Blueprint
from werkzeug import Response

static_blueprint = Blueprint("static", __name__)


@static_blueprint.route("/", methods=["GET"])
def index() -> Union[Response, str]:
    """
    The index page
    :return: The response
    """
    return render_template("static/index.html")


@static_blueprint.route("/about", methods=["GET"])
def about() -> Union[Response, str]:
    """
    The about page/"Impressum" for the website
    :return: The response
    """
    return render_template("static/about.html")


@static_blueprint.route("/privacy", methods=["GET"])
def privacy() -> Union[Response, str]:
    """
    Page containing a privacy disclaimer
    :return: The response
    """
    return render_template("static/privacy.html")
