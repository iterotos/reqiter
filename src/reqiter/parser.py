import argparse
from reqiter.utils import get_version

def init_parser():
    parser = argparse.ArgumentParser(
                    prog='reqiter',
                    description='Toy HTTP/1.1 endpoint brute force tool.')

    parser.add_argument("target")
    parser.add_argument("port", type=int)

    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}",)

    random_group = parser.add_argument_group()
    random_group.add_argument("--threads", type=int, default=8)
    random_group.add_argument("--complete_req", action="store_true")

    template_group = parser.add_argument_group()
    template = template_group.add_mutually_exclusive_group(required=True)
    template.add_argument("-T", "--template")
    template.add_argument("-t", "--templatefile")

    success_group = parser.add_argument_group()
    success = success_group.add_mutually_exclusive_group(required=True)
    success.add_argument("-c", "--code_prefix")
    success.add_argument("-i", "--include")
    success.add_argument("-e", "--exclude")

    output_group = parser.add_argument_group()
    output = output_group.add_mutually_exclusive_group(required=False)
    output.add_argument("-q", "--quiet", action="store_true")
    output.add_argument("-v", "--verbose", action="store_true")
    output.add_argument("-j", "--json", help="produce JSON output",
                        action="store_true")
    
    param_group = parser.add_argument_group()
    param_group.add_argument("-l", "--limit", type=int, default=20, help="Limits the number of generated regex patterns.")

    parser.add_argument("replacements", nargs=argparse.REMAINDER, help=
        "list pairs of replacing values and what to replace them with"
    )

    arguments = parser.parse_args()

    return arguments
