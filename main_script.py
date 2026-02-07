import os
import openai
from scripts.scraper import fetch_trends
from scripts.linkedin_poster import post_to_linkedin

# إعداد OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    print("Step 1: Fetching trends...")
    trends = fetch_trends()
    
    if not trends:
        print("No trends found. Exiting.")
        return

    print(f"Step 2: Generating article for {len(trends)} trends...")
    prompt = f"""
    اكتب مقالاً احترافياً لمنصة LinkedIn باللغة العربية حول أحدث التطورات في مجال الصحة العامة وتكنولوجيا الصحة بناءً على العناوين التالية:
    {chr(10).join(trends)}
    
    الهدف: توعية المتخصصين بآخر المستجدات.
    التنسيق: عنوان جذاب، مقدمة، تحليل موجز، خاتمة تفاعلية، ووسوم (hashtags) مناسبة.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # أو gpt-4
            messages=[{"role": "user", "content": prompt}]
        )
        article = response.choices[0].message.content
        
        print("Step 3: Posting to LinkedIn...")
        post_to_linkedin(article)
        
    except Exception as e:
        print(f"Error in generation or posting: {e}")

if __name__ == "__main__":
    main()
