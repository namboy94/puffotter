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


def byte_string_to_byte_count(byte_string: str) -> int:
    """
    Converts a string representing bytes to a number of bytes.
    For example: "500K" -> 500 000
                 "2.5M" -> 2 500 000
                 "10GB" -> 10 000 000 000
                 "30kb/s" -> 30 000
    :param byte_string: The string to convert
    :return: The amount of bytes
    """
    byte_string = byte_string.lower()

    units = {
        "k": 1000,
        "m": 1000000,
        "g": 1000000000,
        "t": 1000000000000,
        "p": 1000000000000000,
        "e": 1000000000000000000
    }

    for unit in units:
        byte_string = byte_string.replace(unit + "b/s", unit)
        byte_string = byte_string.replace(unit + "b", unit)

    multiplier = 1
    byte_num = ""
    for i, char in enumerate(byte_string):
        if char.isdigit():
            byte_num += char
        else:
            # Unit should be last symbol in string
            if len(byte_string) - 1 != i:
                raise ValueError()
            else:
                try:
                    multiplier = units[char]
                except KeyError:
                    raise ValueError()

    return multiplier * int(byte_num)
