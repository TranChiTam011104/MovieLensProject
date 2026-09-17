import time
from collections import Counter
import requests

# URL public của Cloud Run Service
SERVICE_URL = "https://movielens-api-366360236110.us-central1.run.app"
TOTAL_REQUESTS = 100

print(f"🚀 Bắt đầu gửi {TOTAL_REQUESTS} requests đến: {SERVICE_URL}")
print("Đang kiểm tra phân bổ lưu lượng (Traffic Splitting)... Vui lòng chờ vài giây.\n")

counter = Counter()
revision_counter = Counter()
errors = 0

test_url = f"{SERVICE_URL}/health"
headers = {"Connection": "close"}

for i in range(1, TOTAL_REQUESTS + 1):
    try:
        response = requests.get(test_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            model_used = data.get("model_name") or data.get("model_version") or "unknown_model"
            counter[model_used] += 1
            
            # Ghi nhận thêm revision từ Cloud Run header
            rev = response.headers.get("x-serverless-revision", "unknown_revision")
            revision_counter[rev] += 1
        else:
            errors += 1
            counter[f"HTTP_{response.status_code}"] += 1

    except requests.exceptions.RequestException:
        errors += 1
        counter["Connection_Error"] += 1

    if i % 10 == 0:
        print(f"Đã hoàn thành: {i}/{TOTAL_REQUESTS} requests...")

    time.sleep(0.05)

print("\n" + "=" * 50)
print("📊 KẾT QUẢ PHÂN BỔ THEO MODEL NAME (JSON Body)")
print("=" * 50)
for model, count in counter.items():
    percent = (count / TOTAL_REQUESTS) * 100
    print(f"• {model:<25}: {count:3d} requests ({percent:5.1f}%)")

print("\n" + "=" * 50)
print("📊 ĐỐI CHIẾU THEO REVISION (Cloud Run Header)")
print("=" * 50)
for rev, count in revision_counter.items():
    percent = (count / TOTAL_REQUESTS) * 100
    print(f"• {rev:<35}: {count:3d} requests ({percent:5.1f}%)")

if errors > 0:
    print(f"\n⚠️ Có {errors} request gặp lỗi kết nối hoặc HTTP error!")

print("=" * 50)