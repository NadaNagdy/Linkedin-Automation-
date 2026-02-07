import requests
import os

def post_to_linkedin(content):
    access_token = os.getenv("LINKEDIN_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN") # رقم الـ ID الخاص بك
    
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
    
    response = requests.post(url, headers=headers, json=post_data)
    if response.status_code in [200, 201]:
        print("Successfully posted to LinkedIn!")
    else:
        print(f"Failed to post: {response.status_code}, {response.text}")
