from reqiter.parser import init_parser
from reqiter.utils import (read_if_first_else_second, length_check,
                              loud_print, detect_keys, throw_error)
from reqiter.params import parse_pairs
from reqiter.objects import RequestData, ResponseData
from reqiter.bash import bash
from itertools import product, cycle
import threading
import queue
import json
import sys
from tqdm import tqdm

def main():
    args = init_parser()
    loud_print("Reqiter starting...", (args.quiet, args.json))

    is_tty = sys.stdout.isatty()

    template: str = read_if_first_else_second(args.templatefile, args.template)
    pairs = parse_pairs(args.replacements, (args.quiet, args.json), args.limit)
    keys = pairs.keys()
    values = pairs.values()

    template_keys = detect_keys(template)
    length = length_check(template)
    if "length" in template_keys:
        template_keys.remove("length")
    else:
        throw_error("template must include {length}", code=2)
    arg_keys = set(keys)
    if template_keys-arg_keys:
        args_list = ['-'+arg for arg in template_keys-arg_keys]
        throw_error(f"the following arguments are required: {', '.join(args_list)}", code=2)

    stop_event = threading.Event()
    work_queue: queue.Queue[dict[str, str]] = queue.Queue(maxsize=100)

    def worker():
        while not stop_event.is_set():
            try:
                data = work_queue.get(timeout=0.5)
            except queue.Empty:
                if stop_event.is_set():
                    break
                continue
            if bash(RequestData(
                template,
                data,
                length
            ), ResponseData(
                args.code_prefix,
                args.include,
                args.exclude
            ), args.target, args.port):
                with lock:
                    result["found"] = True
                    result["combination"] = data
                stop_event.set()
            if p is not None:
                p.update(1)
            work_queue.task_done()

    def producer():
        for combo in product(*values):
            if stop_event.is_set():
                break
            current_items = dict(zip(keys, combo))
            try:
                work_queue.put(current_items, timeout=0.2)
            except queue.Full:
                if stop_event.is_set():
                    break
                continue
    
    def stop_all():
        producer_thread.join()
        for t in threads:
            t.join()
        if p is not None:
            p.close()

    threads = []
    result = {"found":False, "combination":None}
    lock = threading.Lock()

    loud_print("\nStarting requests...", (args.quiet, args.json))

    p = None
    if not args.quiet and not args.json and is_tty:
        p = tqdm()

    for _ in range(args.threads if args.threads else 8):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    producer_thread = threading.Thread(target=producer)
    producer_thread.start()

    try:
        stop_event.wait()
    except KeyboardInterrupt:
        stop_event.set()
        stop_all()
        throw_error("All threads stopped. Exiting.")

    stop_all()
    loud_print("\nFinishing...", (args.quiet, args.json), end=" ")

    if args.json:
        if args.complete_req:
            result["request"] = template.format(**result['combination'])
        json.dump(result, sys.stdout)
    elif not result["found"]:
        print("Failure: All candidates were unsuccessful.")
    elif result["combination"]:
        loud_print("Success! The current combination is:", (args.quiet, args.json))
        rescomb = result['combination']
        if args.complete_req:
            print("\n---BEGIN PAYLOAD---\n")
            print(template.format(**result['combination']))
            print("\n---END PAYLOAD---")
        else:
            if isinstance(rescomb, dict) and rescomb.get("length"):
                rescomb.pop("length")
            print(result['combination'])
    sys.exit(0)

if __name__ == "__main__":
    main()
