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

    multiplier_char = byte_string[-1]
    if multiplier_char.isdigit():
        if byte_string.find(".") != -1:
            raise ValueError()
        return int(byte_string)

    try:
        multiplier = units[multiplier_char]
        return int(float(byte_string[:-1]) * multiplier)
    except KeyError:
        raise ValueError()

def human_readable_bytes(
        bytecount: int,
        base_1024: bool = False,
        remove_trailing_zeroes: bool = True
) -> str:
    """
    Converts an amount of bytes into a human-readable string
    :param bytecount: The bytes to convert
    :param base_1024: Whether or not to use 1024 as base (for mebibytes etc)
    :param remove_trailing_zeroes: If set to True, will remove any trailing
                                   zeroes from the string
    :return: The human-readable string
    """
    units = ["K", "M", "G", "T", "P", "E", "Z", "Y"]
    unit_index = -1
    base = 1024 if base_1024 else 1000
    _bytes = float(bytecount)

    while True:
        _bytes /= base
        unit_index += 1

        if int(_bytes) < base or unit_index == len(units) - 1:
            break

    # Formatting
    bytestring = ("%.3f" % _bytes)

    if remove_trailing_zeroes:
        string_index = len(bytestring) - 1
        while bytestring[string_index] == "0":
            string_index -= 1
        bytestring = bytestring[0:string_index + 1]

        if bytestring.endswith("."):
            bytestring = bytestring[0:-1]

    i = "i" if base_1024 else ""
    return bytestring + units[unit_index] + i + "B"
