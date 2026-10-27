import sys
import os
import json
import random
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

from scraper import fetch_trends
from linkedin_poster import post_to_linkedin, post_comment
from opportunity_scraper import scrape_opportunities, scrape_medical_conferences 

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
    

    # Load history
    history_file = "history.json"
    try:
        with open(history_file, "r") as hf:
            posted_urls = json.load(hf)
    except (FileNotFoundError, json.JSONDecodeError):
        posted_urls = []

    def is_unposted(item):
        url = item.get("link") or item.get("url") or item.get("name", "")
        return url not in posted_urls


    
    # 2. Fetch Opportunities

    print("🔍 Fetching opportunities...")
    opportunities = scrape_opportunities(queries=search_queries)
    conferences = scrape_medical_conferences()

    if trends: trends = [t for t in trends if is_unposted(t)]
    if opportunities: opportunities = [o for o in opportunities if is_unposted(o)]
    if conferences: conferences = [c for c in conferences if is_unposted(c)]
    
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
    post_type = None
    if "--type=research" in sys.argv:
        post_type = "research"
    elif "--type=pubmed" in sys.argv:
        post_type = "pubmed"
    elif "--type=opportunity" in sys.argv:
        post_type = "opportunity"
    elif "--type=conference" in sys.argv:
        post_type = "conference"
    elif "--type=tool" in sys.argv:
        post_type = "tool"


    if post_type == "tool":
        all_tools = config.get("research_tools", [])
        unposted_tools = [t for t in all_tools if t.get("name") not in posted_urls]
        available_tools = unposted_tools if unposted_tools else all_tools
        if available_tools:
            selected_tool = random.choice(available_tools)
            selected_article = {"title": selected_tool["name"], "source": "Tool", "company": selected_tool["description"], "url": ""}
        else:
            selected_article = {}
    elif post_type in ["pubmed", "research"]:
        pubmed_articles = [t for t in trends if "pubmed" in t.get("source", "").lower() or "pubmed" in t.get("title", "").lower()]
        if post_type == "pubmed":
            selected_article = random.choice(pubmed_articles) if pubmed_articles else {}
        else:
            selected_article = random.choice(pubmed_articles) if pubmed_articles else (random.choice(trends) if trends else {})
    elif post_type == "conference" and conferences:
        selected_article = random.choice(conferences)
    elif post_type == "opportunity" and combined_content:
        opps = [item for item in combined_content if item not in trends]
        
        def is_egypt_or_remote(item):
            text = f"{item.get('location', '')} {item.get('title', '')} {item.get('company', '')}".lower()
            return any(k in text for k in ['egypt', 'cairo', 'giza', 'alexandria', 'mansoura', 'assiut', 'tanta', 'monufya', 'remote', 'telework', 'online', 'virtual', 'work from home'])

        # Priority 1: Fresh Egypt or Remote opportunities posted this month
        egypt_remote_fresh = [o for o in opps if is_egypt_or_remote(o) and o.get('is_fresh')]
        # Priority 2: Any Egypt or Remote opportunities
        egypt_remote_all = [o for o in opps if is_egypt_or_remote(o)]
        # Priority 3: Any fresh opportunities
        fresh_opps = [o for o in opps if o.get('is_fresh')]

        if egypt_remote_fresh:
            selected_article = random.choice(egypt_remote_fresh)
        elif egypt_remote_all:
            selected_article = random.choice(egypt_remote_all)
        elif fresh_opps:
            selected_article = random.choice(fresh_opps)
        else:
            selected_article = random.choice(opps) if opps else random.choice(combined_content)
    else:
        # Fallback to random if type not specified or list empty
        all_options = combined_content + conferences
        selected_article = random.choice(all_options) if all_options else {}
    

    article_title = selected_article.get("title")
    if not article_title:
        print("⚠️ No fresh content available for this post type! Everything has already been posted.")
        sys.exit(0)
    
    article_url = selected_article.get("link") or selected_article.get("url", "")

    source = selected_article.get("source", "Trend")
    company = selected_article.get("company", "N/A")
    location = selected_article.get("location", "N/A")
    
    print(f"🎯 Selected Content: {article_title} ({source})")
    print(f"🔗 URL: {article_url}")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    post_content = ""

    if openai_api_key:
        print("🤖 Generating content with OpenAI...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            system_role = prompts.get("system_role", "You are a friendly, helpful colleague.")
            
            # Determine post type
            is_conference = '[Conference]' in article_title or source == 'WHO'
            is_tool = source == 'Tool'
            is_pubmed = source == 'PubMed' or 'pubmed' in article_url.lower() or 'Research (PubMed)' in article_title
            is_opportunity = (source in ['Wuzzuf', 'ReliefWeb', 'ScholarshipsAds', 'Internships'] or \
                             any(k in article_title.lower() for k in ['job', 'internship', 'scholarship'])) and not is_conference and not is_tool and not is_pubmed
            
            if is_tool:
                 user_prompt_template = prompts.get("tool_generation", "Write about this tool: {title}")
                 prompt = user_prompt_template.replace("{title}", article_title)\
                                              .replace("{description}", company)
            elif is_conference:
                 user_prompt_template = prompts.get("conference_generation", "Write a post about this conference: {title}")
                 prompt = user_prompt_template.replace("{title}", article_title)\
                                              .replace("{company}", company)\
                                              .replace("{location}", location)
            elif is_opportunity:
                 user_prompt_template = prompts.get("opportunity_generation", "Write a post about this opportunity: {title}")
                 prompt = user_prompt_template.replace("{title}", article_title)\
                                              .replace("{company}", company)\
                                              .replace("{location}", location)
            elif is_pubmed:
                 abstract = selected_article.get("description", "")
                 journal = company if company != "N/A" else "Medical Journal"
                 prompt = (
                     f"Act as a professional medical and health researcher. Write an engaging dual-language LinkedIn post (English and Arabic) highlighting this new scientific research study published in {journal}:\n"
                     f"Study Title: {article_title}\n"
                     + (f"Abstract / Summary: {abstract}\n" if abstract else "")
                     + "\nStructure must be exactly as follows:\n"
                     "English Section:\n"
                     "[Explain the core objective, key findings/results of the study, and practical public health or clinical implications in a clear, compelling narrative. Keep it engaging, professional, and accessible to health professionals.]\n\n"
                     "---\n"
                     "Arabic Section:\n"
                     "[Explain the exact same content in clear, natural Arabic. Focus on the core findings, importance of the study, and practical impact on health.]\n\n"
                     "Make sure to literally print the text 'English Section:' and 'Arabic Section:' before the respective paragraphs."
                 )
            else:
                 user_prompt_template = prompts.get("content_generation", "Summarize this: '{article_title}'")
                 prompt = user_prompt_template.replace("{article_title}", article_title)
            
            completion = client.chat.completions.create(
                model=settings.get("openai_model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ]
            )
            
            ai_text = completion.choices[0].message.content.strip()
            
            # Construct hashtags
            hashtags = "\n".join(posting_config.get("hashtags", ["#Tech", "#News"]))
            
            if is_conference:
                post_content = f"📅 **Upcoming Conference / مؤتمر قادم**\n\n{ai_text}\n\n{hashtags}"
            elif is_opportunity:
                post_content = f"🚀 **New Opportunity / فرصة جديدة**\n\n{ai_text}\n\n{hashtags}"
            elif is_pubmed:
                post_content = f"🔬 **New Research / دراسة بحثية جديدة**\n\n{ai_text}\n\n{hashtags}"
            else:
                post_content = f"🎓 **Global Insights / رؤى عالمية**\n\n{ai_text}\n\n{hashtags}"
            
        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            print("⚠️ Skipping LinkedIn post to avoid publishing incomplete content.")
            return
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
            comment_text = f"🔗 Link: {article_url}"
             # If opportunity, emphasize applying
            if source in ['Wuzzuf', 'ReliefWeb', 'ScholarshipsAds', 'Internships']:
                 comment_text = f"🚀 للتقديم / Apply here: {article_url}"
            elif source == 'WHO':
                 comment_text = f"📅 للتسجيل والمشاركة / Register here: {article_url}"
            elif is_pubmed or 'pubmed' in article_url.lower():
                 comment_text = f"📄 رابط البحث الكامل / Read Full Paper: {article_url}"
            
            post_comment(post_id, comment_text, final_author)
            
        # Save to history
        posted_urls.append(article_url or article_title)
        with open(history_file, "w") as hf:
            json.dump(posted_urls, hf)

            
    else:
        print("❌ Failed to post.")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        # Exit with code 1 only if LinkedIn token is clearly invalid (401)
        if response is not None and response.status_code == 401:
            print("🔑 Token is expired or invalid. Please regenerate your LinkedIn token.")
            sys.exit(1)
        # For other errors (duplicate post, etc.) don't crash the workflow
        sys.exit(0)

if __name__ == "__main__":
    main()
