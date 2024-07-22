import os.path

import typer
import subprocess

app = typer.Typer()
HOME_DIR = os.path.expanduser("~")
PROJECT_PATH = os.path.join(HOME_DIR, "/github/wrp_read_ai")

@app.command()
def update():
    print("executing git pull...")
    print("restarting readai_worker.service systemd unit...")

@app.command()
def restart():
    subprocess.run(
        ["git", "pull"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_PATH
    )

if __name__ == "__main__":
    app()