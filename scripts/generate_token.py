import requests
import webbrowser
import os
from flask import Flask, request
import urllib.parse

app = Flask(__name__)

# --- Configuration (Defaults from config.js) ---
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "77n8awe98j70ci")
REDIRECT_URI = "http://localhost:5500/callback.html" 
SCOPE = "openid profile email w_member_social r_organization_social w_organization_social"

# Global variable to store Client Secret
CLIENT_SECRET = None

@app.route('/callback.html')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"<h1>Error: {error}</h1>"
    
    if code:
        print(f"\n✅ Authorization Code Received: {code}")
        
        # Exchange Code for Token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        
        try:
            # LinkedIn expects application/x-www-form-urlencoded, requests sends this by default with 'data='
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            json_response = response.json()
            access_token = json_response.get("access_token")
            expires_in = json_response.get("expires_in")
            
            print(f"\n🎉 SUCCESS! Access Token: {access_token}")
            print(f"Expires in: {expires_in} seconds.")
            
            return f"""
            <h1>Authentication Successful!</h1>
            <p>Your Access Token has been printed to the console.</p>
            <p>You can close this window now.</p>
            <textarea style="width:100%; height:100px;">{access_token}</textarea>
            """
            
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error exchanging token: {e}")
            print(f"Response: {response.text}")
            return f"<h1>Error exchanging token</h1><p>{response.text}</p>"
            
    return "<h1>No code received.</h1>"

def main():
    global CLIENT_SECRET, CLIENT_ID
    print("\n--- LinkedIn Token Generator ---")
    
    client_id_input = input(f"Enter your LinkedIn Client ID (press Enter to keep default '{CLIENT_ID}'): ").strip()
    if client_id_input:
        CLIENT_ID = client_id_input
    
    # 1. Get Client Secret from User or Env
    CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
    if not CLIENT_SECRET:
        CLIENT_SECRET = input("Enter your LinkedIn Client Secret: ").strip()
    
    if not CLIENT_SECRET:
        print("❌ Client Secret is required!")
        return

    # 2. Construct Authorization URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"\n🚀 Opening browser to: {auth_url}")
    webbrowser.open(auth_url)
    
    print("\nStarting local server on port 5500 to listen for callback...")
    # Run Flask server securely
    app.run(port=5500)

if __name__ == "__main__":
    main()
