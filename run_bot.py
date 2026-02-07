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
    
    # Debug Token
    token = os.getenv("LINKEDIN_TOKEN")
    if token:
        print(f"🔑 Token loaded in run_bot.py (Length: {len(token)})")
        print(f"🔑 Token start: {token[:4]}...")
    else:
        print("❌ Token is NONE in run_bot.py")

    # 1. Fetch Trends
    print("🔍 Fetching latest trends...")
    trends = fetch_trends()
    
    if not trends:
        print("⚠️ No trends found. Exiting.")
        return

    print(f"✅ Found {len(trends)} articles.")
    
    # 2. Select Article & Generate Content (AI Persona)
    if not trends:
        print("⚠️ No trends found. Exiting.")
        return

    # Pick the first article (simplest logic for now)
    selected_article = trends[0]
    print(f"🎯 Selected Article: {selected_article}")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    post_content = ""

    if openai_api_key:
        print("🤖 Generating content with OpenAI (Teacher Persona)...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            prompt = (
                f"You are a friendly and wise teacher who loves explaining complex topics using simple, relatable analogies. "
                f"Explain this headline/topic to a general audience on LinkedIn: '{selected_article}'. "
                f"Make it engaging, educational, and easy to understand. "
                f"End with a thought-provoking question. "
                f"Keep it under 150 words. "
                f"Do not use the phrase 'Imagine a...'. "
            )
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_text = completion.choices[0].message.content.strip()
            post_content = f"🎓 **Today's Lesson**\n\n{ai_text}\n\n#Learning #TechExplained #Innovation #Education"
            
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            post_content = f"📌 **Topic of the Day**\n\n{selected_article}\n\n(AI explanation failed, falling back to headline.)"
    else:
        print("⚠️ OPENAI_API_KEY not found. Skipping AI generation.")
        post_content = f"📌 **Topic of the Day**\n\n{selected_article}\n\n#TechNews #Health"

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
        if response:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        sys.exit(1) # Exit with error for CI/CD

if __name__ == "__main__":
    main()
