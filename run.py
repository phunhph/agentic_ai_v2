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
    print("🚀 ĐỐI TƯỢNG: HỆ THỐNG AGENTIC CRM ĐANG KHỞI ĐỘNG")
    print("="*50 + "\n")

    # 1. Khởi chạy Flask API (Backend)
    print("📡 Bước 1: Khởi động Backend API (Flask)...")
    api_process = subprocess.Popen([sys.executable, "apps/api/app.py"], env=env)

    # Đợi một chút để API khởi động xong
    time.sleep(2)

    # 2. Khởi chạy Streamlit UI (Frontend)
    print("💻 Bước 2: Khởi động Frontend UI (Streamlit)...")
    # Chúng ta giả định cổng mặc định là 8501
    ui_url = "http://localhost:8501"
    
    try:
        # Khởi chạy streamlit
        ui_process = subprocess.Popen(["streamlit", "run", "apps/web/ui.py", "--server.port", "8501"], env=env)
        
        # Đợi Streamlit khởi động rồi tự động mở trình duyệt
        time.sleep(5)
        print(f"\n🌍 Đang mở giao diện tại: {ui_url}")
        webbrowser.open(ui_url)
        
        print("\n✅ HỆ THỐNG ĐÃ SẴN SÀNG!")
        print(f"👉 Giao diện người dùng: {ui_url}")
        print(f"👉 Backend API: http://localhost:5000")
        print("\nNhấn Ctrl+C để dừng toàn bộ hệ thống.")

        # Giữ script chạy để quản lý các process
        ui_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng toàn bộ hệ thống...")
        api_process.terminate()
        ui_process.terminate()
        print("👋 Đã dừng thành công.")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
        api_process.terminate()

if __name__ == "__main__":
    run_system()
