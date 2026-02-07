import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_linkedin():
    token = os.getenv("LINKEDIN_TOKEN")
    # محاولة تجربة 3 مسارات مختلفة للحصول على الهوية (حسب إصدار الـ API الخاص بك)
    endpoints = [
        "https://api.linkedin.com/v2/me",
        "https://api.linkedin.com/v2/userinfo",
        "https://api.linkedin.com/v1/people/~:(id)"
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("--- LinkedIn Diagnosis Report ---")
    for url in endpoints:
        try:
            res = requests.get(url, headers=headers)
            print(f"Testing {url} -> Status: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                # تجربة استخراج الـ ID من مختلف الأماكن المتوقعة
                user_id = data.get('id') or data.get('sub')
                if user_id:
                    print(f"✅ Found your URN: {user_id}")
                    return user_id
            else:
                print(f"❌ Response: {res.text}")
        except Exception as e:
            print(f"💥 Error testing {url}: {e}")
            
    return None

if __name__ == "__main__":
    check_linkedin()
