import requests
import os

def post_to_linkedin(content):
    access_token = os.getenv("LINKEDIN_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")
    
    if not access_token or not person_urn:
        print("❌ نقص في البيانات: LINKEDIN_TOKEN أو LINKEDIN_PERSON_URN غير موجود")
        return None

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    post_data = {
        "author": f"urn:li:person:{person_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    try:
        return requests.post(url, headers=headers, json=post_data)
    except Exception as e:
        print(f"❌ خطأ اتصال: {e}")
        return None
