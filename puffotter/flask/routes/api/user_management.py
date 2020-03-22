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

from typing import Dict, Any
from flask import Blueprint, request
from flask_login import login_required
from puffotter.crypto import generate_random, generate_hash
from puffotter.flask.base import db
from puffotter.flask.Config import Config
from puffotter.flask.db.User import User
from puffotter.flask.db.ApiKey import ApiKey
from puffotter.flask.exceptions import ApiException
from puffotter.flask.routes.decorators import api, api_login_required

user_management_api_blueprint = Blueprint("user_management_api", __name__)


@user_management_api_blueprint.route(
    "/api/v1/key", methods=["POST", "DELETE"]
)
@api
def api_key() -> Dict[str, Any]:
    """
    Allows users to request a new API key or revoke an existing API key
    :return: The JSON response
    """
    data = request.get_json()
    if request.method == "POST":
        username = data["username"]
        password = data["password"]
        user = User.query.filter_by(username=username).first()

        if user is None:
            raise ApiException("user does not exist", 401)
        elif not user.confirmed:
            raise ApiException("user is not confirmed", 401)
        elif not user.verify_password(password):
            raise ApiException("password is incorrect", 401)
        else:
            key = generate_random(32)
            hashed = generate_hash(key)
            _api_key = ApiKey(user=user, key_hash=hashed)
            db.session.add(_api_key)
            db.session.commit()

            return {
                "api_key": "{}:{}".format(_api_key.id, key),
                "expiration": (
                        int(_api_key.creation_time)
                        + Config.MAX_API_KEY_AGE
                ),
                "user": user.__json__(True)
            }

    else:  # request.method == "DELETE"
        key = data["api_key"]
        _api_key = ApiKey.query.get(key.split(":", 1)[0])

        if _api_key is None:
            raise ApiException("API key does not exist", 401)
        elif not _api_key.verify_key(key):
            raise ApiException("API key not valid", 401)
        else:
            db.session.delete(_api_key)
            db.session.commit()
            return {}


@user_management_api_blueprint.route("/api/v1/authorize", methods=["GET"])
@api_login_required
@login_required
@api
def api_authorize() -> Dict[str, Any]:
    """
    Allows a user to check if an API key is authorized or not
    :return: None
    """
    return {}  # Checks done by @login_required
