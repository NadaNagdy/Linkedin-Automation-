import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def post_to_linkedin(content, author_urn=None):
    access_token = os.getenv("LINKEDIN_TOKEN")
    default_person_urn = os.getenv("LINKEDIN_PERSON_URN")
    
    if not access_token:
        print("❌ نقص في البيانات: LINKEDIN_TOKEN غير موجود")
        return None, None

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
        return None, None

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
        response = requests.post(url, headers=headers, json=post_data, timeout=30)
        return response, final_author
    except Exception as e:
        print(f"❌ خطأ اتصال: {e}")
        return None, final_author

def post_comment(object_urn, comment_text, author_urn):
    """
    Posts a comment on a LinkedIn share or UGC post.
    """
    access_token = os.getenv("LINKEDIN_TOKEN")
    if not access_token:
        print("❌ Token missing for comment.")
        return None

    # URL encode the URN for the endpoint
    # The endpoint is /socialActions/{urn}/comments
    # If URN has colons, they might need encoding, but requests usually handles it if passed in URL path correctly?
    # Actually, LinkedIn API expects the URN as part of the path.
    # Example: https://api.linkedin.com/v2/socialActions/urn%3Ali%3Ashare%3A123/comments
    
    import urllib.parse
    encoded_urn = urllib.parse.quote(object_urn)
    url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}/comments"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    payload = {
        "actor": author_urn,
        "message": {
            "text": comment_text
        }
    }
    
    try:
        print(f"💬 Posting comment on {object_urn} as {author_urn}...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return response
    except Exception as e:
        print(f"❌ Error posting comment: {e}")
        return None
