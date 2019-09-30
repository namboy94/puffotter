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

from typing import List


def yn_prompt(
        message: str,
        make_sure: bool = True,
        case_sensitive: bool = False
) -> bool:
    """
    Creates a yes/no prompt
    :param message: The message to display
    :param make_sure: Continuously prompts if the response is neither
                      'y' or 'n' until it is.
                      If false, every input besides 'y' will result in the
                      return value being False
    :param case_sensitive: Whether or not the prompt should be case-sensitive
    :return: True if the user specified 'y', else False
    """
    resp = input(message + " (y|n): ").strip()
    if not case_sensitive:
        resp = resp.lower()

    if resp == "y":
        return True
    elif resp == "n" or not make_sure:
        return False
    else:
        return yn_prompt(message, make_sure, case_sensitive)


def selection_prompt(objects: List[object]) -> List[object]:
    """
    Prompts the user for a selection from a list of objects
    :param objects: The objects to show
    :return: The selection of objects
    """

    fill = len(str(len(objects)))
    for i, obj in enumerate(objects):
        print("[{}] {}".format(str(i + 1).zfill(fill), str(obj)))

    while True:

        selection = input("Selection: ").split(",")
        valid = True
        selected_objects = []

        for item in selection:

            try:
                start_index = int(item)
                end_index = start_index
            except IndexError:
                try:
                    start, end = item.split("-", 1)
                    start_index = int(start)
                    end_index = int(end)
                except (IndexError, ValueError):
                    valid = False
                    break

            for i in range(start_index, end_index + 1):
                try:
                    selected_objects.append(objects[i - 1])
                except IndexError:
                    valid = False
                    break

        if not valid:
            print("Invalid selection")
        else:
            return selected_objects
