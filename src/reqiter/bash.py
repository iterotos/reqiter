from reqiter.objects import RequestData, ResponseData
from reqiter.utils import throw_error
import socket

infos = None

def bash_init(target: str, port: int):
    global infos
    infos = socket.getaddrinfo(target, port, socket.AF_INET, socket.SOCK_STREAM)

def create_ipv4_connection(addr, port):
    if infos is None:
        bash_init(addr, port)
    assert infos is not None
    af, socktype, proto, _, sa = infos[0]

    sock = socket.socket(af, socktype, proto)
    sock.connect(sa)
    return sock

def bash(request: RequestData, response: ResponseData, target: str, port: int, debug: bool = False) -> bool:
    with create_ipv4_connection(target, port) as sock:
        complete_length = sum([len(i) for i in request.replacements.values()])
        request.replacements["length"]=str(request.body_length+complete_length)

        request_content = request.template.format(**request.replacements).encode()
        sock.sendall(request_content)
        if debug:
            print(request_content)

        resp = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            resp += chunk

        resp_text = resp.decode("iso-8859-1")
        header, body = resp_text.split("\r\n\r\n", 1)
        status_line = header.split("\r\n", 1)[0]
        if response.code_prefix:
            return status_line.split()[1].startswith(response.code_prefix)
        elif response.include:
            return response.include in body
        elif response.exclude:
            return response.exclude not in body
        else:
            throw_error("cannot determine validity of response")
            exit()
