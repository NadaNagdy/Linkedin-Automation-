#!/usr/bin/env python3
"""
سكريبت لجلب Organization IDs والنشر على صفحة الشركة
"""

import os
import requests
import json
from dotenv import load_dotenv

# تحميل المتغيرات من .env
load_dotenv()

# الـ Access Token بتاعك
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    print("❌ خطأ: مفيش Access Token في ملف .env")
    print("   حطّي LINKEDIN_ACCESS_TOKEN في ملف .env")
    exit(1)

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json',
    'LinkedIn-Version': '202406',
    'X-Restli-Protocol-Version': '2.0.0'
}

def get_organizations():
    """جلب كل الـ Organizations اللي عندك صلاحيات عليها"""
    print("🔍 بجلب الـ Organizations اللي عندك صلاحيات عليها...\n")
    
    # استخدام API endpoint الصحيح
    url = "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organization~(id,localizedName,vanityName),roleAssignee,role,state))"
    
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        organizations = []
        
        print("=" * 60)
        print("✅ الشركات اللي عندك صلاحيات Admin عليها:")
        print("=" * 60 + "\n")
        
        for element in data.get('elements', []):
            org_data = element.get('organization~', {})
            org_id = org_data.get('id', 'N/A')
            org_name = org_data.get('localizedName', 'N/A')
            vanity_name = org_data.get('vanityName', 'N/A')
            role = element.get('role', 'N/A')
            state = element.get('state', 'N/A')
            
            organizations.append({
                'id': org_id,
                'name': org_name,
                'vanity_name': vanity_name,
                'role': role,
                'state': state
            })
            
            print(f"📌 اسم الشركة: {org_name}")
            print(f"   Organization ID: {org_id}")
            print(f"   Vanity Name: {vanity_name}")
            print(f"   الصلاحية: {role}")
            print(f"   الحالة: {state}")
            print()
        
        return organizations
    else:
        print(f"❌ خطأ في جلب الـ Organizations: {response.status_code}")
        print(f"Response: {response.text}\n")
        return []

def test_post_to_organization(org_id, org_name):
    """تجربة النشر على صفحة الشركة"""
    print("=" * 60)
    print(f"🚀 بجرّب أنشر post على: {org_name}")
    print(f"   Organization ID: {org_id}")
    print("=" * 60 + "\n")
    
    # تحضير الـ post data بالطريقة الصحيحة
    # LinkedIn API v2 format
    post_data = {
        "author": f"urn:li:organization:{org_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "🧪 Test post from LinkedIn Automation Bot - Testing organization posting! 🚀"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    print("📤 بعمل POST request...")
    print(f"Request Body:\n{json.dumps(post_data, indent=2)}\n")
    
    response = requests.post(url, headers=HEADERS, json=post_data)
    
    if response.status_code in [200, 201]:
        print("✅ نجح! تم النشر على صفحة الشركة بنجاح! 🎉\n")
        response_data = response.json()
        post_id = response_data.get('id', 'N/A')
        print(f"Post ID: {post_id}\n")
        return True
    else:
        print(f"❌ فشل النشر - Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:\n{response.text}\n")
        
        # تحليل الخطأ
        try:
            error_data = response.json()
            if 'message' in error_data:
                print(f"💡 رسالة الخطأ: {error_data['message']}")
            if 'serviceErrorCode' in error_data:
                print(f"💡 Service Error Code: {error_data['serviceErrorCode']}")
        except:
            pass
        
        return False

def main():
    print("\n" + "=" * 60)
    print("🔧 LinkedIn Organization Post Fixer")
    print("=" * 60 + "\n")
    
    # 1. جلب الـ Organizations
    organizations = get_organizations()
    
    if not organizations:
        print("❌ مفيش organizations متاحة!")
        return
    
    # 2. تجربة النشر على كل organization
    print("=" * 60)
    print("🧪 بجرّب النشر على كل الـ Organizations...")
    print("=" * 60 + "\n")
    
    for org in organizations:
        success = test_post_to_organization(org['id'], org['name'])
        
        if success:
            print(f"✅ استخدمي Organization ID: {org['id']}")
            print(f"   في السكريبت بتاعك بدل 111716442\n")
            break
        else:
            print(f"⏭️  نجرّب الـ Organization التانية...\n")
    
    print("=" * 60)
    print("✨ انتهى الفحص!")
    print("=" * 60)

if __name__ == "__main__":
    main()
