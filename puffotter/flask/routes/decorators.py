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

from functools import wraps
from typing import Callable
from flask import jsonify, make_response, request
from werkzeug.exceptions import Unauthorized
from puffotter.flask.exceptions import ApiException


def api(func: Callable) -> Callable:
    """
    Decorator that handles common API patterns and ensures that
    the JSON response will always follow a certain pattern
    :param func: The function to wrap
    :return: The wrapper function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Tries running the function and checks for errors
        :param args: args
        :param kwargs: kwargs
        :return: The JSON response including an appropriate HTTP status code
        """
        code = 200
        response = {"status": "ok"}

        try:
            is_json = request.content_type.startswith("application/json") \
                      and request.is_json \
                      and isinstance(request.get_json(silent=True), dict)
            if request.method in ["POST", "PUT", "DELETE"] and not is_json:
                raise ApiException(
                    "Not in JSON format", 400
                )

            response["data"] = func(*args, **kwargs)

        except (KeyError, TypeError, ValueError, ApiException) as e:

            response["status"] = "error"

            if isinstance(e, ApiException):
                code = e.status_code
                response["reason"] = e.reason

            else:
                code = 400
                response["reason"] = "Bad Request: {}".format(type(e).__name__)

        return make_response(jsonify(response), code)

    return wrapper


def api_login_required(func: Callable) -> Callable:
    """
    Decorator to make unauthorized API calls respond with JSON properly
    :param func: The function to wrap
    :return: The wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Checks if flask-login throws an Unauthorized exception. If so,
        re-wrap the response in JSON
        :param args: The function arguments
        :param kwargs: The function keyword arguments
        :return: The newly wrapped response,
                 or just the plain response if authorized
        """

        try:
            resp = func(*args, **kwargs)
            return resp
        except Unauthorized:
            return make_response(
                jsonify({"status": "error", "reason": "Unauthorized"}), 401
            )

    return wrapper
