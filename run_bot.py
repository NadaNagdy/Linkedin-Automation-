import sys
import os
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from scraper import fetch_trends
from linkedin_poster import post_to_linkedin

# Load environment variables
load_dotenv(override=True)

def main():
    print("🚀 Starting LinkedIn Automation Bot...")
    
    # 1. Fetch Trends
    print("🔍 Fetching latest trends...")
    trends = fetch_trends()
    
    if not trends:
        print("⚠️ No trends found. Exiting.")
        return

    print(f"✅ Found {len(trends)} articles.")
    
    # 2. Format Post
    # Basic formatting - can be improved
    post_content = "🌟 Daily Health & Tech Trends 🌟\n\n"
    for item in trends:
        post_content += f"📌 {item}\n"
    
    post_content += "\n#HealthTech #Innovation #PublicHealth #Automation #Python"
    
    print("\n📝 Generated Post Content:")
    print(post_content)
    print("-" * 30)

    # 3. Post to LinkedIn
    # Check if a specific author URN is set (e.g. for Company Page), otherwise default to Profile
    target_urn = os.getenv("LINKEDIN_AUTHOR_URN") 
    
    print(f"🚀 Posting to LinkedIn ({target_urn if target_urn else 'Default Profile'})...")
    response = post_to_linkedin(post_content, author_urn=target_urn)
    
    if response and response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
        print(f"Post ID: {response.json().get('id')}")
    else:
        print("❌ Failed to post.")
        sys.exit(1) # Exit with error for CI/CD

if __name__ == "__main__":
    main()
