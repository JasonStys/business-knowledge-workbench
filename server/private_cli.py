# @index-begin
# @symbol function/class: data_directory L39
# @symbol variable/parameter: base L44
# @symbol function/class: parent_guard L52
# @symbol variable/parameter: server L52
# @symbol variable/parameter: pid L54
# @symbol variable/parameter: started L55
# @symbol variable/parameter: parent L59
# @symbol function/class: main L73
# @symbol variable/parameter: parser L75
# @symbol variable/parameter: args L80
# @symbol variable/parameter: bundle L83
# @symbol variable/parameter: ui L84
# @symbol variable/parameter: listener L85
# @symbol variable/parameter: port L88
# @symbol variable/parameter: app L89
# @symbol variable/parameter: thread L109
# @symbol variable/parameter: deadline L113
# @symbol variable/parameter: url L118
# @index-end
"""Jason Stys: token-free local account website and frozen service; never execute uploaded documents."""

import argparse
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import psutil
import uvicorn

os.environ.pop("KB_LEGACY_MODE", None)
from server.private_api import create_private_app


def data_directory() -> Path:
    """Return a new per-OS private root outside Git/installation and all legacy controller data."""
    if os.environ.get("KBW_ACCOUNT_DATA"):
        return Path(os.environ["KBW_ACCOUNT_DATA"])
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "BusinessKnowledgeWorkbenchAccounts"


def parent_guard(server):
    """An exact native parent PID/create-time monitor requests graceful sealing if its launcher disappears."""
    pid = os.environ.get("KBW_PARENT_PID")
    started = os.environ.get("KBW_PARENT_STARTED")
    if not pid:
        return
    try:
        parent = psutil.Process(int(pid))
        if started and abs(parent.create_time() - float(started)) > 0.02:
            server.should_exit = True
            return
        while not server.should_exit:
            try:
                parent.wait(timeout=0.5)
                server.should_exit = True
            except psutil.TimeoutExpired:
                pass
    except (psutil.NoSuchProcess, ValueError):
        server.should_exit = True


def main():
    """Prebind literal loopback, start the private app, and print only a nonsecret website URL."""
    parser = argparse.ArgumentParser(description="Business Knowledge Workbench - Jason Stys")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--data", type=Path)
    parser.add_argument("--ui", type=Path)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if args.port and not 1024 <= args.port <= 65535:
        raise SystemExit("Port must be automatic (0) or 1024..65535")
    bundle = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    ui = args.ui or (bundle / "ui" if getattr(sys, "frozen", False) else bundle / "dist")
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", args.port))
    listener.listen(128)
    port = listener.getsockname()[1]
    app = create_private_app(
        args.data or data_directory(),
        port,
        ui,
        os.environ.get("KBW_LAUNCH_TOKEN", ""),
        os.environ.get("KBW_LAUNCH_NONCE", ""),
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            access_log=False,
            log_level="warning",
            proxy_headers=False,
            limit_concurrency=50,
            timeout_keep_alive=5,
        )
    )
    app.state.shutdown = lambda: setattr(server, "should_exit", True)
    thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=False)
    thread.start()
    threading.Thread(target=parent_guard, args=(server,), daemon=True).start()
    try:
        deadline = time.monotonic() + 30
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not server.started:
            raise SystemExit("Account service failed to start; preserve private recovery data")
        url = f"http://127.0.0.1:{port}/"
        print("Business Knowledge Workbench - Jason Stys:", url, flush=True)
        print("Local only. Documents are encrypted when the workspace is locked.", flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        server.should_exit = True
        thread.join(timeout=30)
    finally:
        server.should_exit = True
        listener.close()


if __name__ == "__main__":
    main()
