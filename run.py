import subprocess
import time
import sys
import os
import webbrowser

def run_system():
    # Cấu hình môi trường để bỏ qua email prompt của Streamlit
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["PYTHONPATH"] = os.getcwd()

    print("\n" + "="*50)
    print("STARTING AGENTIC CRM SYSTEM")
    print("="*50 + "\n")

    # 1. Khởi chạy Flask API (Backend)
    print("Step 1: Starting Backend API (Flask)...")
    api_process = subprocess.Popen([sys.executable, "apps/api/app.py"], env=env)

    # Đợi một chút để API khởi động xong
    time.sleep(3)

    # 2. Khởi chạy Streamlit UI (Frontend)
    print("Step 2: Starting Frontend UI (Streamlit)...")
    ui_url = "http://localhost:8501"
    
    try:
        # Sử dụng python -m streamlit để đảm bảo chạy đúng môi trường
        ui_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "apps/web/ui.py", "--server.port", "8501"], env=env)
        
        # Đợi Streamlit khởi động rồi tự động mở trình duyệt
        time.sleep(5)
        print(f"\nOpening UI at: {ui_url}")
        webbrowser.open(ui_url)
        
        print("\nSYSTEM IS READY!")
        print(f"User Interface: {ui_url}")
        print(f"Backend API: http://localhost:5000")
        print("\nPress Ctrl+C to stop.")

        # Giữ script chạy để quản lý các process
        while True:
            time.sleep(1)
            if api_process.poll() is not None:
                print("Backend API stopped unexpectedly.")
                break
            if ui_process.poll() is not None:
                print("Frontend UI stopped unexpectedly.")
                break
                
    except KeyboardInterrupt:
        print("\nStopping system...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        api_process.terminate()
        if 'ui_process' in locals():
            ui_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    run_system()
