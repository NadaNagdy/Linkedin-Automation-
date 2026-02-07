import sys
import os
import json
import random
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from scraper import fetch_trends
from linkedin_poster import post_to_linkedin, post_comment
from opportunity_scraper import scrape_opportunities 

# Load environment variables
load_dotenv(override=True)

def load_config():
    config_path = os.path.join(os.getcwd(), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ config.json not found. Using defaults.")
        return {}
    except json.JSONDecodeError:
        print("❌ Error decoding config.json. Check syntax.")
        return {}

def main():
    config = load_config()
    prompts = config.get("prompts", {})
    settings = config.get("settings", {})
    posting_config = config.get("posting", {})
    search_queries = config.get("search_queries", {})
    
    print(f"🚀 Starting {config.get('project_name', 'LinkedIn Automation Bot')}...")
    
    # Debug Token
    token = os.getenv("LINKEDIN_TOKEN")
    if token:
        print(f"🔑 Token loaded (Length: {len(token)})")
    else:
        print("❌ Token is NONE")

    # 1. Fetch Trends
    print("🔍 Fetching latest trends...")
    trends = fetch_trends()
    
    # 2. Fetch Opportunities
    print("🔍 Fetching opportunities...")
    opportunities = scrape_opportunities(queries=search_queries)
    
    combined_content = []
    
    # Prioritize "Fresh" opportunities
    if opportunities:
        print(f"✅ Found {len(opportunities)} new opportunities.")
        fresh_opps = [op for op in opportunities if op.get('is_fresh')]
        other_opps = [op for op in opportunities if not op.get('is_fresh')]
        
        print(f"🔥 Fresh Opportunities: {len(fresh_opps)}")
        
        # Add fresh opportunities first
        combined_content.extend(fresh_opps)
        # Then others
        combined_content.extend(other_opps)
    
    # Add trends at the end (lower priority if opportunities exist)
    if trends:
        combined_content.extend(trends)
    
    if not combined_content:
        print("⚠️ No content found to post. Exiting.")
        return

    print(f"✅ Total items available: {len(combined_content)}")

    # 3. Select Content & Generate Post
    # Pick the first fresh item, or random if they are all similar priority?
    # For now, pick the first one which is likely the freshest opportunity.
    selected_article = combined_content[0] 
    
    article_title = selected_article.get("title", "Unknown Title")
    article_url = selected_article.get("link") or selected_article.get("url", "")
    source = selected_article.get("source", "Trend")
    
    print(f"🎯 Selected Content: {article_title} ({source})")
    print(f"🔗 URL: {article_url}")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    post_content = ""

    if openai_api_key:
        print("🤖 Generating content with OpenAI...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            system_role = prompts.get("system_role", "You are a helpful assistant.")
            user_prompt_template = prompts.get("content_generation", "Summarize this: '{article_title}'")
            
            # Format the prompt with the article title
            prompt = user_prompt_template.replace("{article_title}", article_title)
            
            completion = client.chat.completions.create(
                model=settings.get("openai_model", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_text = completion.choices[0].message.content.strip()
            
            # Construct hashtags
            hashtags = " ".join(posting_config.get("hashtags", ["#Tech", "#News"]))
            
            post_content = f"🎓 **Update / تحديث**\n\n{ai_text}\n\n{hashtags}"
            
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            post_content = f"📌 **Topic of the Day**\n\n{article_title}\n\n(AI generation failed.)"
    else:
        print("⚠️ OPENAI_API_KEY not found. Skipping AI generation.")
        post_content = f"📌 **Topic of the Day**\n\n{article_title}\n\n#TechNews"

    print("\n📝 Generated Post Content:")
    print(post_content)
    print("-" * 30)

    # 4. Post to LinkedIn
    author_key = posting_config.get("author_urn_env_key", "LINKEDIN_AUTHOR_URN")
    target_urn = os.getenv(author_key)
    
    print(f"🚀 Posting to LinkedIn ({target_urn if target_urn else 'Default Profile'})...")
    
    response, final_author = post_to_linkedin(post_content, author_urn=target_urn)
    
    if response and response.status_code == 201:
        print("✅ Successfully posted to LinkedIn!")
        post_id = response.json().get('id')
        print(f"Post ID: {post_id}")
        
        # 5. Post Comment with Link
        if article_url and final_author:
            print("💬 Adding link in comments...")
            comment_text = f"🔗 Read the full details here: {article_url}"
            post_comment(post_id, comment_text, final_author)
            
    else:
        print("❌ Failed to post.")
        if response:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
