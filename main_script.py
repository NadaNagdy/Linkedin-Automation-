import requests
import os
token = os.getenv("LINKEDIN_TOKEN")
r = requests.get("https://api.linkedin.com/v2/me", headers={"Authorization": f"Bearer {token}"})
print(f"Your URN is: {r.json().get('id')}")
