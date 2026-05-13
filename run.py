from __future__ import annotations
import subprocess
import sys
from time import sleep


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "api"
    if target == "api":
        print("Starting Flask API on http://0.0.0.0:8000")
        subprocess.run([sys.executable, "apps/api/app.py"])
    elif target == "ui":
        print("Starting Streamlit UI")
        subprocess.run(["streamlit", "run", "apps/web/streamlit_app.py"])
    elif target == "all":
        print("Starting both Flask API and Streamlit UI")
        api_proc = subprocess.Popen([sys.executable, "apps/api/app.py"])
        sleep(2)
        ui_proc = subprocess.Popen(["streamlit", "run", "apps/web/streamlit_app.py"])

        try:
            while True:
                if api_proc.poll() is not None or ui_proc.poll() is not None:
                    break
                sleep(1)
        except KeyboardInterrupt:
            api_proc.terminate()
            ui_proc.terminate()
            print("Shutting down API and UI")
        return api_proc.poll() or ui_proc.poll() or 0
    else:
        print("Usage: python run.py [api|ui|all]")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
