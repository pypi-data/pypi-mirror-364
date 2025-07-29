import base64
import json
import os
from contextlib import suppress
from typing import Any, cast
from urllib.parse import urlencode

import httpx
import requests  # type: ignore[import-untyped]  # noqa: F401
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, render_template, request, session

from devopness import DevopnessClient

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

LARAVEL_API_URL = cast(str, os.getenv("LARAVEL_API_URL"))
LARAVEL_EXTERNAL_AUTH_URL = cast(str, os.getenv("LARAVEL_EXTERNAL_AUTH_URL"))

if not LARAVEL_API_URL or not LARAVEL_EXTERNAL_AUTH_URL:
    raise ValueError(
        "LARAVEL_API_URL and LARAVEL_EXTERNAL_AUTH_URL"
        " environment variables must be set"
    )


@app.route("/login")
def login() -> Any:  # noqa: ANN401
    oauth_next = request.args.get("next")
    if not oauth_next:
        return jsonify(
            {
                "error": "invalid_request",
                "error_description": "The `next` parameter is required",
            }
        )

    session["oauth_next"] = oauth_next

    oauth_error = request.args.get("error") or ""

    # If the error parameter is not a base64-encoded string, ignore it
    with suppress(Exception):
        oauth_error = base64.b64decode(oauth_error).decode("utf-8")

    return render_template("login.html", error=oauth_error)


@app.route("/authenticate", methods=["POST"])
def authenticate() -> Any:  # noqa: ANN401
    oauth_next = session.get("oauth_next")
    if not oauth_next:
        return jsonify(
            {
                "error": "session_expired",
                "error_description": "Session expired",
            }
        ), 400

    oauth_action = request.form["action"]
    if oauth_action not in ["allow", "deny"]:
        return jsonify(
            {
                "error": "invalid_request",
                "error_description": "The `action` parameter is invalid",
            }
        ), 400

    try:
        decoded_next = base64.b64decode(oauth_next).decode("utf-8")
        json_next = json.loads(decoded_next)

    except Exception:
        msg = "The `next` parameter is not a valid base64-encoded JSON string"

        return redirect(f"/login?error={msg}&next={oauth_next}")

    if oauth_action == "deny":
        return redirect(
            json_next["redirect_uri"]
            + "?error=access_denied"
            + (f"&state={json_next['state']}" if "state" in json_next else "")
        )

    try:
        devopness = DevopnessClient(
            {
                "base_url": LARAVEL_API_URL,
            }
        )

        devopness.users.login_user(
            {
                "email": str(request.form["email"]),
                "password": str(request.form["password"]),
            }
        )

    except Exception as e:
        err = str(e).replace(" See validation errors for details.", "")
        if err.index("Message") > 0:
            err = err[err.index("Message") :]

        msg = base64.b64encode(err.encode("utf-8")).decode("utf-8")

        return redirect(f"/login?error={msg}&next={oauth_next}")

    try:
        with httpx.Client(follow_redirects=False) as client:
            response = client.get(
                LARAVEL_EXTERNAL_AUTH_URL + "?" + urlencode(json_next),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "devopness-mcp-server",
                    "Authorization": f"Bearer {devopness.access_token}",
                },
            )

        # Filtering out header 'transfer-encoding' to avoid Nginx errors.
        # The Devopness API response includes 'transfer-encoding' and 'content-length'
        # headers, and returning them causes Nginx to emit an error:
        #       Upstream sent "Content-Length" and "Transfer-Encoding" headers
        #       at the same time while reading response header from upstream
        filtered_headers = {
            k: v
            for k, v in response.headers.items()
            if k.lower() not in {"transfer-encoding"}
        }

        return Response(
            response.content,
            status=response.status_code,
            headers=filtered_headers,
        )

    except Exception as e:
        return redirect(f"/login?error={e}&next={oauth_next}")


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))

    app.run(host, port)
