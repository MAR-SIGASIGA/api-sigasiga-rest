import os
import subprocess

def run_uwsgi():
    command = [
        "uwsgi",
        "--http", "0.0.0.0:5000",
        "--module", "main:app",
        "--master",
        "--processes", "4",
        "--threads", "2",
        "--env", "MODE=production"
    ]
    subprocess.run(command)

if __name__ == "__main__":
    mode = os.getenv("MODE", "development")
    if mode == "development":
        from main import create_app
        app = create_app()
        app.run(debug=True, host="0.0.0.0", port=5000)
    elif mode == "production":
        run_uwsgi()