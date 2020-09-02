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

from bokkichat.entities.Address import Address
from bokkichat.entities.message.TextMessage import TextMessage
from puffotter.flask.base import db
from puffotter.flask.Config import Config
from puffotter.flask.db.ModelMixin import ModelMixin
from puffotter.flask.db.User import User


class TelegramChatId(ModelMixin, db.Model):
    """
    Model that describes the 'telegram_chat_ids' SQL table
    Maps telegram chat ids to users
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "telegram_chat_ids"
    """
    The name of the table
    """

    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"),
        nullable=False
    )
    """
    The ID of the user associated with this telegram chat ID
    """

    user: User = db.relationship("User", back_populates="telegram_chat_id")
    """
    The user associated with this telegram chat ID
    """

    chat_id: str = db.Column(db.String(255), nullable=False)
    """
    The telegram chat ID
    """

    def send_message(self, message_text: str):
        """
        Sends a message to the telegram chat
        :param message_text: The message text to send
        :return: None
        """
        address = Address(self.chat_id)
        message = TextMessage(
            Config.TELEGRAM_BOT_CONNECTION.address,
            address,
            message_text
        )
        Config.TELEGRAM_BOT_CONNECTION.send(message)
