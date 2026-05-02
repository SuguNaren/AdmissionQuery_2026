import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".runtime-venv"
REQUIREMENTS_FILE = ROOT / "requirements.txt"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE_FILE = ROOT / ".env.example"
SERVE_FLAG = "--serve"
DEV_FLAG = "--dev"


def _venv_python():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _run(cmd):
    subprocess.check_call(cmd, cwd=ROOT)


def _ensure_env_file():
    if not ENV_FILE.exists() and ENV_EXAMPLE_FILE.exists():
        shutil.copyfile(ENV_EXAMPLE_FILE, ENV_FILE)
        print("Created .env from .env.example")


def _bootstrap():
    python_in_venv = _venv_python()

    if not python_in_venv.exists():
        print("Creating isolated virtual environment...")
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])

    print("Installing project dependencies...")
    _run([str(python_in_venv), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])

    _ensure_env_file()

    passthrough = [arg for arg in sys.argv[1:] if arg not in {SERVE_FLAG}]
    _run([str(python_in_venv), str(ROOT / "run.py"), SERVE_FLAG, *passthrough])


def _serve():
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from app import app

    host = os.getenv("APP_HOST", os.getenv("HOST", "0.0.0.0"))
    port = int(os.getenv("APP_PORT", os.getenv("PORT", "8086")))
    debug = DEV_FLAG in sys.argv or os.getenv("FLASK_DEBUG", "0").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if debug:
        app.run(host=host, port=port, debug=True)
        return

    try:
        from waitress import serve
    except ImportError:
        print("waitress is not installed yet, falling back to the Flask development server.")
        app.run(host=host, port=port, debug=False)
        return

    threads = int(os.getenv("APP_THREADS", "6"))
    serve(app, host=host, port=port, threads=threads)


def main():
    if SERVE_FLAG in sys.argv:
        _serve()
        return

    _bootstrap()


if __name__ == "__main__":
    main()
