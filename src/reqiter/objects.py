from dataclasses import dataclass

@dataclass
class RequestData:
    template: str
    replacements: dict[str, str]
    body_length: int

@dataclass
class ResponseData:
    code_prefix: str|None
    include: str|None
    exclude: str|None
