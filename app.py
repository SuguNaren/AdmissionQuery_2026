import os
import uuid
from collections import defaultdict
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file, session

from database.db import save_chat
from models.nlp_model import pdf_response, resolve_course_selection


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "smc-chatbot-session-secret")
APP_ROOT = Path(__file__).resolve().parent

MAX_SESSION_TURNS = 8
session_histories = defaultdict(list)


def _session_id():
    if "chat_session_id" not in session:
        session["chat_session_id"] = str(uuid.uuid4())
    return session["chat_session_id"]


def _session_history():
    return session_histories[_session_id()]


def _remember_turn(user_message, bot_reply):
    history = _session_history()
    history.append({"user": user_message, "bot": bot_reply})
    if len(history) > MAX_SESSION_TURNS:
        del history[:-MAX_SESSION_TURNS]


def _env_flag(name, default="0"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


@app.after_request
def add_cors_headers(response):
    # Allow local preview pages and localhost web servers to call the Flask endpoints.
    origin = request.headers.get("Origin")
    response.headers["Access-Control-Allow-Origin"] = "*" if not origin or origin == "null" else origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Vary"] = "Origin"

    if request.headers.get("Access-Control-Request-Private-Network") == "true":
        response.headers["Access-Control-Allow-Private-Network"] = "true"

    return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/widget-embed")
def widget_embed():
    return render_template("widget-embed.html")


@app.route("/online-app-home")
def online_app_home():
    return send_file(APP_ROOT / "OnlineApp_Home.html")


@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        user_input = request.json["message"]
        history = list(_session_history())

        # Reuse the current browser session's recent turns for follow-up questions.
        bot_reply = pdf_response(user_input, history=history)
        _remember_turn(user_input, bot_reply)

        # Save to database, but do not block the chatbot if DB credentials are not ready.
        try:
            save_chat(user_input, bot_reply)
        except Exception as db_error:
            print("Database logging error:", db_error)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Something went wrong. Please try again."})


@app.route("/resolve-course", methods=["POST", "OPTIONS"])
def resolve_course():
    if request.method == "OPTIONS":
        return ("", 204)

    try:
        user_input = request.json["query"]
        return jsonify(resolve_course_selection(user_input))
    except Exception as e:
        print("Resolve course error:", e)
        return jsonify({"status": "error"})


@app.route("/reset-chat", methods=["POST", "OPTIONS"])
def reset_chat():
    if request.method == "OPTIONS":
        return ("", 204)

    session_histories.pop(_session_id(), None)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    host = os.getenv("APP_HOST", os.getenv("HOST", "0.0.0.0"))
    port = int(os.getenv("APP_PORT", os.getenv("PORT", "8086")))
    debug = _env_flag("FLASK_DEBUG")
    app.run(host=host, port=port, debug=debug)
