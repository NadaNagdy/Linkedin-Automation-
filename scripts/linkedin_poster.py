import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def post_to_linkedin(content, author_urn=None):
    access_token = os.getenv("LINKEDIN_TOKEN")
    default_person_urn = os.getenv("LINKEDIN_PERSON_URN")
    
    if not access_token:
        print("❌ نقص في البيانات: LINKEDIN_TOKEN غير موجود")
        return None

    print(f"🔑 Token in poster: {len(access_token)} chars")

    # Determine the author URN
    if author_urn:
        # If the user provided a full URN (e.g. urn:li:organization:123), use it.
        # If they provided just an ID, we might need to know if it's person or organization.
        # For simplicity, let's assume if it doesn't start with 'urn:', we default to person? 
        # No, better to force full URN or handle logic outside. 
        # But to be safe for existing calls:
        if not author_urn.startswith("urn:"):
             # Fallback or assume person? Let's check if it's the person URN from env
             final_author = f"urn:li:person:{author_urn}"
        else:
             final_author = author_urn
    elif default_person_urn:
        final_author = f"urn:li:person:{default_person_urn}"
    else:
        print("❌ نقص في البيانات: LINKEDIN_PERSON_URN أو author_urn غير موجود")
        return None

    print(f"🚀 Author URN: {final_author}")

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    post_data = {
        "author": final_author,
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
        return requests.post(url, headers=headers, json=post_data, timeout=30)
    except Exception as e:
        print(f"❌ خطأ اتصال: {e}")
        return None
