import re

from pydantic import BaseModel


def remove_parentheses(input_string: str) -> str:
    """
    Remove parentheses using a recursive regex approach.
    This repeatedly removes the innermost parentheses until none remain.
    """
    # Pattern to match innermost parentheses (no nested parentheses inside)
    pattern = re.compile(r"\([^()]*\)")

    while pattern.search(input_string):
        input_string = pattern.sub("", input_string)

    return input_string


def camel_to_snake_case(input_string: str) -> str:
    result = [input_string[0].lower()]
    for char in input_string[1:]:
        if char.isupper():
            result.extend(["_", char.lower()])
        else:
            result.append(char)
    return "".join(result)


def model_name_to_snake(model: type[BaseModel]) -> str:
    return camel_to_snake_case(model.__name__)
