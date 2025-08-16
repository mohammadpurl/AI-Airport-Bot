import requests
import json

# Test data - exactly what you provided
test_data = {
    "messages": [
        {
            "id": "1755320084411",
            "text": "سلام می‌خوام به نیویورک سفر کنم",
            "sender": "CLIENT",
        },
        {"id": "1755320102152", "text": "فرودگاه امام خمینی", "sender": "CLIENT"},
        {"id": "1755320113088", "text": "خروجی از فرودگاه", "sender": "CLIENT"},
        {"id": "1755320124988", "text": "۲۸ مرداد ۱۴۰۴", "sender": "CLIENT"},
        {
            "id": "1755320129384",
            "text": "تعداد دقیق مسافران چند نفر است؟",
            "sender": "AVATAR",
        },
    ]
}

# Test the debug endpoint first
print("Testing debug endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/debug-extract-info",
        json=test_data,
        headers={"Content-Type": "application/json"},
    )
    print(f"Debug endpoint status: {response.status_code}")
    print(f"Debug endpoint response: {response.text}")
except Exception as e:
    print(f"Debug endpoint error: {e}")

print("\n" + "=" * 50 + "\n")

# Test the main endpoint
print("Testing main endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/api/v1/extract-info",
        json=test_data,
        headers={"Content-Type": "application/json"},
    )
    print(f"Main endpoint status: {response.status_code}")
    print(f"Main endpoint response: {response.text}")
except Exception as e:
    print(f"Main endpoint error: {e}")
