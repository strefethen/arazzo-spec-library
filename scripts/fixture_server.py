"""Strict, ordered loopback HTTP expectations for the real Arazzo CLI."""

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlsplit


def match_request(expected, method, target, headers, body):
    url = urlsplit(target)
    actual_query = parse_qs(url.query, keep_blank_values=True)
    wanted_query = {
        key: value if isinstance(value, list) else [str(value)]
        for key, value in expected.get("query", {}).items()
    }
    if method != expected["method"] or unquote(url.path) != expected["path"]:
        raise AssertionError(f"request target: {method} {unquote(url.path)} != "
                             f"{expected['method']} {expected['path']}")
    if actual_query != wanted_query:
        raise AssertionError(f"query: {actual_query!r} != {wanted_query!r}")
    lower_headers = {key.lower(): value for key, value in headers.items()}
    for key in expected.get("absent_headers", []):
        if key.lower() in lower_headers:
            raise AssertionError("forbidden request header present")
    for key, value in expected.get("headers", {}).items():
        if lower_headers.get(key.lower()) != value:
            raise AssertionError(f"header {key!r} did not match")
    if "body" in expected:
        if json.loads(body) != expected["body"]:
            raise AssertionError("JSON request body did not match")
    elif body:
        raise AssertionError("unexpected request body")


@contextmanager
def fixture_server(requests, read_fixture):
    """Serve only the supplied expectations; never proxy or contact upstream."""
    state = {"index": 0, "errors": []}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.handle_expectation()

        def do_POST(self):
            self.handle_expectation()

        def do_PUT(self):
            self.handle_expectation()

        def do_PATCH(self):
            self.handle_expectation()

        def do_DELETE(self):
            self.handle_expectation()

        def do_HEAD(self):
            self.handle_expectation()

        def do_OPTIONS(self):
            self.handle_expectation()

        def log_message(self, *_args):
            pass

        def handle_expectation(self):
            with lock:
                try:
                    if state["index"] >= len(requests):
                        raise AssertionError("unexpected extra HTTP request")
                    expected = requests[state["index"]]
                    length = int(self.headers.get("Content-Length", 0))
                    if length > 1024 * 1024:
                        raise AssertionError("fixture request body exceeded 1 MiB")
                    body = self.rfile.read(length)
                    match_request(expected, self.command, self.path, self.headers, body)
                    response = expected["response"]
                    data = (read_fixture(response["fixture"]) if "fixture" in response
                            else response["body"])
                    state["index"] += 1
                    status = response.get("status", 200)
                    payload = b"" if status == 204 else json.dumps(data).encode()
                    self.send_response(status)
                    if status != 204:
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(payload)))
                    for key, value in response.get("headers", {}).items():
                        if status == 204 and key.lower() in {"content-length", "transfer-encoding"}:
                            continue
                        self.send_header(key, value)
                    self.end_headers()
                    if self.command != "HEAD":
                        self.wfile.write(payload)
                except (AssertionError, ValueError, KeyError, OSError) as error:
                    state["errors"].append(str(error))
                    self.send_error(500, "fixture expectation mismatch")

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def assert_consumed(requests, state):
    if state["errors"]:
        raise AssertionError("; ".join(state["errors"]))
    if state["index"] != len(requests):
        raise AssertionError(f"consumed {state['index']} of {len(requests)} requests")
