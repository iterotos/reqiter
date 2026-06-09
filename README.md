# Reqiter
Toy HTTP/1.1 request endpoint bruteforce tool. Mostly meant as a demonstration against endpoints which do not throttle requests or have any sort of security measure whatsoever. Not for use in non sandboxed/CTF situations.

## What does Reqiter do?
It's in the name. **Req**uest **Iter**ator.  
Given a template with parameters and CLI arguments, it will iterate through every combination of parameters until a success/nonfailure is reached.

To run it, you need a few things:
- A template which must provide the entire request with defined parameters enclosed by curly braces.
- A series of CLI arguments denoting what to replace the parameters with.
- A success condition that can either be a HTTP response code, or a string that must/cannot be in the response.
- The host name and port.

Optionally, verbosity/output and threads can also be controlled through CLI arguments.

## Installation
```sh
git clone https://github.com/iterotos/reqiter.git
cd reqiter
pip install .
```
A PyPI release is not planned as this is just a small project.

## Parameters
A template file must include the following in the header:
```http
Content-Length: {length}
```
This is to dynamically calculate the length of the body. The length of the parameters will be computed during runtime.

But for it to be useful, it should also include parameters in the header/body to replace. For example:
```http
{{"username":"{user}","password":"{password}"}}
```
By passing arguments `-user` and `-password`, you may specify what to substitute these parameters with. Parameters take the following forms:
- `-param str:test` The str: prefix denotes a raw string. If the string contains newlines, it will be split into lines and iterated through.
- `-param file:path` The file: prefix denotes a filepath that can be read from. Similarly, if it contains newlines, it will also be iterated through.

A `regex:` option expanding non-infinite regexes and a `range:` option functioning similarly to a for loop are planned.

## Examples
```sh
reqiter -t template.txt -c 2 localhost 3000 -user str:admin -password file:rockyou.txt
```
Example usage, targeting `localhost:3000`, accepting any http response code beginning with 2, trying a request for every password in `rockyou.txt` with the user `admin`.

## Limitations
As mentioned before, Reqiter is just a small project aiming for ease-of-use. As such, it **cannot** do the following:
- **Send non HTTP/1.1 requests.** Due to the underlying library being `sockets`, it could technically send others. However, the `-c`/`--code_prefix` option would break, so you'll be stuck with the other success conditions. Also, it has not been tested with non HTTP/1.1 requests and support is not planned either.
- **Attack real endpoints.** Reqiter is not built for that sort of task. It does not aim to provide extremely high performance/throughput, and it's defaults are on the polite end (8 threads). It also does not take any possible endpoint security measures into account.
