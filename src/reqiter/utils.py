from importlib.metadata import PackageNotFoundError, version
from string import Formatter
import sys

def read_if_first_else_second(first: str, second: str) -> str:
    try:
        if first:
            with open(first, "rb") as file:
                return file.read().decode("iso-8859-1")
        else:
            return second
    except FileNotFoundError as e:
        throw_error(f"file {first} not found")
        exit()

def loud_print(text, quiet: tuple[bool, bool], end = None, flush:bool = False):
    if not quiet[0] and not quiet[1]:
        print(text, end=end, flush=flush)

def return_fields(template: str):
    formatter = Formatter()
    data: list[tuple[str, str | None, str | None, str | None]] = []
    for field in formatter.parse(template):
        data.append(field)
    return data

def detect_keys(template: str):
    fields = return_fields(template)
    field_names = set()
    for literal_text, field_name, format_spec, conversion in fields:
        if field_name:
            field_names.add(field_name)
    return field_names

def length_check(template: str):
    lines = template.splitlines()
    if not lines[0].strip().endswith("HTTP/1.1"):
        throw_error("template is not a HTTP/1.1 request", code=2)
    body = template.split("\r\n\r\n", 1)[1]
    fields: list[tuple] = return_fields(body)
    return len(''.join([field[0] for field in fields]))

def throw_error(error: str, code: int = 1):
    print("Reqiter: error:", error)
    sys.exit(code)

def get_version():
    try:
        VERSION = version(__package__ or "reqiter")
    except PackageNotFoundError:
        VERSION = "unknown"
    return VERSION
