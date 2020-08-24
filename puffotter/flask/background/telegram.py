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


# noinspection PyPackageRequirements
from telegram.error import Conflict
from puffotter.flask.base import app
from puffotter.flask.Config import Config
from bokkichat.entities.message.TextMessage import TextMessage


def telegram_whoami():
    """
    Specifies the background behaviour of the telegram bot
    By default, the bot listens to /whoami messages
    and answers with the telegram chat ID
    :return: None
    """
    telegram = Config.TELEGRAM_BOT_CONNECTION

    def handler(_, msg):
        if msg.is_text():
            msg: TextMessage = msg

            if msg.body == "/whoami":
                sender = telegram.address
                receiver = msg.sender
                telegram.send(
                    TextMessage(sender, receiver, receiver.address))

    try:
        telegram.loop(handler)
    except Conflict:
        app.logger.warning("It seems that two instances of the telegram "
                           "bot are running")
