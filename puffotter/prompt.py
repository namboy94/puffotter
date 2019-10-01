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

from typing import List, Any, Callable, Optional


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


def prompt_comma_list(
        message: str,
        primitive_type: Callable[[str], Any] = str,
        min_count: int = 0,
        no_empty: bool = True
) -> List[Any]:
    """
    Prompts the user for a comma-separated list
    :param message: The message to display
    :param primitive_type: The primitive type of the elements in the list
    :param min_count: The minimum amount of elements to be provided by the user
    :param no_empty: Removes any empty strings
    :return: The result of the prompt
    """
    while True:
        try:
            response = input(message)
            result = list(map(lambda x: x.strip(), response.split(",")))

            if "" in result and no_empty:
                result.remove("")
            result = list(map(lambda x: primitive_type(x), result))

            if len(result) < min_count:
                print("Not enough values")
                raise ValueError()
            else:
                return result

        except (ValueError, TypeError):
            print("Invalid input")


def prompt(
        prompt_text: str = "",
        default: Optional[Any] = None,
        _type: Callable[[str], Any] = str,
        required: bool = True
) -> Optional[Any]:
    """
    Generic prompt with configuration options
    :param prompt_text: The text to display before the prompt
    :param default: A default value to use if the user responds with ''
    :param _type: The type of the object prompted. Must take a single string
                  as a parameter
    :param required: Whether or not as response is required
    :return: The prompt result. May be None if required is False
    """
    if default is not None:
        prompt_text += " {}".format(str(default))
    prompt_text += ":"

    response = input(prompt_text).strip()
    while response == "" and default is None:
        response = input(prompt_text).strip()

    if response == "" and default is not None:
        return default
    elif response == "":
        if required:
            return prompt(prompt_text, default, _type, required)
        else:
            return None
    else:
        try:
            return _type(response)
        except (TypeError, ValueError):
            return prompt(prompt_text, default, _type, required)