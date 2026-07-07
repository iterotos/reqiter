from reqiter.utils import loud_print, throw_error
import exrex
import re

def parse_pairs(pairs: list[str], quietness: tuple[bool, bool], limit: int = 20) -> dict[str, list[str]]:
    if len(pairs)%2==1:
        throw_error("odd number of replacement arguments", code=2)
    result: dict[str, list[str]] = {}
    for i in range(0, len(pairs), 2):
        if pairs[i][0]!="-":
            throw_error(f"replacement arguments are malformed", code=2)
        param_name=pairs[i][1:] # strip the dash
        content=pairs[i+1]
        if content.startswith("str:"):
            result[param_name] = content[4:].splitlines()   # first four chars are str:
        elif content.startswith("file:"):
            file_result = parse_file(content[5:], quietness)
            result[param_name] = file_result if file_result else []
        elif content.startswith("regex:"):
            regexp_result = parse_regex(content[6:], quietness, limit)
            result[param_name] = regexp_result if regexp_result else []
        else:
            throw_error(f"replacement arguments are malformed", code=2)
    return result

def parse_file(filename: str, quietness: tuple[bool, bool]):
    try:
        with open(filename, "rb", buffering=1024*1024) as file:    # first five chars are file:
            loud_print(f"Reading file {filename}:", quiet=quietness, end="", flush=True)
            file_list = []
            try:
                file_list = file.read().decode("iso-8859-1").splitlines()
            except KeyboardInterrupt:
                print()
                throw_error(f"Reading of file {filename} cancelled. Exiting.")
            loud_print(" done!", quietness)
            return file_list
    except FileNotFoundError as e:
        throw_error(f"file {filename} not found")

def parse_regex(regexp: str, quietness: tuple[bool, bool], limit: int):
    try:
        loud_print(f"Parsing regex {regexp}:", quiet=quietness, end="", flush=True)
        regexp_lists: list[str] = [i for i in exrex.generate(regexp, limit=limit+1)]
        loud_print(" done!", quietness)
        if len(regexp_lists)>limit:
            print(f"Warning: all regex patterns after #{limit} were ignored.")
        return regexp_lists[:limit]
    except re.error:
        print()
        throw_error(f"Regex pattern {regexp} could not be parsed.")