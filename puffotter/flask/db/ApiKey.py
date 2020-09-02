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
from puffotter.flask.db.User import User
from puffotter.flask.base import db
from puffotter.flask.Config import Config
from puffotter.flask.db.ModelMixin import ModelMixin
from puffotter.crypto import verify_password


class ApiKey(ModelMixin, db.Model):
    """
    Model that describes the 'api_keys' SQL table
    An ApiKey is used for API access using HTTP basic auth
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "api_keys"
    """
    The name of the table
    """

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    """
    The ID of the user associated with this API key
    """

    user: User = db.relationship("User", back_populates="api_keys")
    """
    The user associated with this API key
    """

    key_hash: str = db.Column(db.String(255), nullable=False)
    """
    The hash of the API key
    """

    creation_time: int = \
        db.Column(db.Integer, nullable=False, default=time.time)
    """
    The time at which this API key was created as a UNIX timestamp
    """

    def has_expired(self) -> bool:
        """
        Checks if the API key has expired.
        API Keys expire after 30 days
        :return: True if the key has expired, False otherwise
        """
        return time.time() - self.creation_time > Config.MAX_API_KEY_AGE

    def verify_key(self, key: str) -> bool:
        """
        Checks if a given key is valid
        :param key: The key to check
        :return: True if the key is valid, False otherwise
        """
        try:
            _id, api_key = key.split(":", 1)
            if int(_id) != self.id:
                return False
            else:
                return verify_password(api_key, self.key_hash)
        except ValueError:
            return False
