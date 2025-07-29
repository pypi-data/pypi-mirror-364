import msvcrt
import os
from os import system

import requests


def box(string: str) -> str:
    raw_lines = string.split("\n")
    stripped_lines = [line.strip() for line in raw_lines]
    if not stripped_lines:
        return "+--+\n|  |\n+--+"
    width = max((len(line) for line in stripped_lines), default=0)
    border = "+" + "-" * (width + 2) + "+"
    boxed_lines = [
        f"| {line.ljust(width)} |" if line else "|" + " " * (width + 2) + "|"
        for line in stripped_lines
    ]
    return f"{border}\n" + "\n".join(boxed_lines) + f"\n{border}"


def deltemp():
    import sys

    for var in tuple(sys._getframe(1).f_locals):
        if var[0] == "_":
            sys._getframe(1).f_locals.pop(var, None)


def getch():
    try:
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):  # Special keys (arrows, function keys, etc.)
            msvcrt.getch()  # Consume the next byte
            return ""  # Or return a specific value for special keys
        return ch.decode("utf-8")
    except Exception:
        return ""


def getchar(d, arg):
    return d.get(arg, d["DEFAULTS"][arg])


def clsscr(*args):
    system("cls" if os.name == "nt" else "clear")


def loadstring(code=None, url=None):
    """
    Execute a string of Python code or code fetched from a URL, similar to Lua's loadstring().

    Args:
        code (str, optional): A string containing Python code to execute.
        url (str, optional): A URL pointing to a text file containing Python code.

    Returns:
        dict: The globals dictionary containing variables/functions defined during execution.

    Raises:
        ValueError: If neither code nor url is provided, or if both are provided.
        Exception: For errors during code execution or URL fetching.
    """
    if (code is None and url is None) or (code is not None and url is not None):
        raise ValueError("Provide either a code string or a URL, not both or neither.")

    # Initialize an empty globals dictionary to avoid polluting the main namespace
    globals_dict = {}

    try:
        if url:
            # Fetch code from the provided URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            code = response.text

        # Execute the code in the globals dictionary
        exec(code, globals_dict)

        return globals_dict

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch code from URL: {str(e)}")
    except SyntaxError as e:
        raise Exception(f"Syntax error in code: {str(e)}")
    except Exception as e:
        raise Exception(f"Error executing code: {str(e)}")
