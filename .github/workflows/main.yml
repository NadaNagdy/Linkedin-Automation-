import requests
import os

token = os.getenv("LINKEDIN_TOKEN")
# استخدام userinfo بدلاً من me لأنها الأحدث في نظام الصلاحيات
response = requests.get(
    "https://api.linkedin.com/v2/userinfo", 
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    # الـ id هنا هو الـ Person URN اللي محتاجينه
    print(f"✅ Your Person URN is: {response.json().get('sub')}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
