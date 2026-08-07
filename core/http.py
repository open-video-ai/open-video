"""Tiny stdlib HTTP helper shared by the engine adapter and the VLM judge."""
import json
import urllib.request


def post_json(url: str, payload: dict, headers: dict | None = None,
              timeout: float = 30.0) -> dict:
    """POST a JSON payload, return the parsed JSON response. Raises on HTTP errors."""
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())
