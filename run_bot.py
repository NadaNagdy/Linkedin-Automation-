import sys
import os
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from scraper import fetch_trends
from linkedin_poster import post_to_linkedin, post_comment

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
    # Pick the first article
    selected_article = trends[0]
    article_title = selected_article.get("title", "Unknown Title")
    article_url = selected_article.get("url", "")
    
    print(f"🎯 Selected Article: {article_title}")
    print(f"🔗 URL: {article_url}")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    post_content = ""

    if openai_api_key:
        print("🤖 Generating content with OpenAI (Dual Language Teacher)...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            prompt = (
                f"You are a friendly teacher who explains complex topics using simple analogies. "
                f"I need a dual-language post (English and Arabic) about this headline: '{article_title}'. "
                f"\n\nStructure:\n"
                f"1. English Explanation (Simple, engaging, 4-5 sentences).\n"
                f"2. A separator line (---).\n"
                f"3. Arabic Explanation (Same tone, simplified, using analogies).\n"
                f"\nDo not mention 'Imagine a...'. Keep it educational and professional yet accessible."
            )
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_text = completion.choices[0].message.content.strip()
            post_content = f"🎓 **Global Insights / رؤى عالمية**\n\n{ai_text}\n\n#HealthTech #Innovation #Education #PublicHealth #Research"
            
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            post_content = f"📌 **Topic of the Day**\n\n{article_title}\n\n(AI generation failed.)"
    else:
        print("⚠️ OPENAI_API_KEY not found. Skipping AI generation.")
        post_content = f"📌 **Topic of the Day**\n\n{article_title}\n\n#TechNews #Health"

    print("\n📝 Generated Post Content:")
    print(post_content)
    print("-" * 30)

    # 3. Post to LinkedIn
    target_urn = os.getenv("LINKEDIN_AUTHOR_URN") 
    
    print(f"🚀 Posting to LinkedIn ({target_urn if target_urn else 'Default Profile'})...")
    response, final_author = post_to_linkedin(post_content, author_urn=target_urn)
    
    if response and response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
        post_id = response.json().get('id')
        print(f"Post ID: {post_id}")
        
        # 4. Post Comment with Link
        if article_url and final_author:
            print("💬 Adding link in comments...")
            comment_text = f"🔗 Read the full research here: {article_url}"
            post_comment(post_id, comment_text, final_author)
            
    else:
        print("❌ Failed to post.")
        if response:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
