import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.linkedin_poster import post_to_linkedin, post_comment

load_dotenv(override=True)

def main():
    print("🚀 Preparing Weekly Scientific Digest LinkedIn Post...")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY is missing!")
        return

    client = OpenAI(api_key=openai_api_key)
    
    system_role = (
        "You are a premier science communicator and health-tech editor writing for an audience of "
        "clinicians, researchers, scientists, and healthcare innovators on LinkedIn."
    )
    
    prompt = """
Write a high-impact, inspiring dual-language LinkedIn post summarizing this week's most significant breakthroughs and events in global science, medicine, and health technology.

Feature these major developments from this week:
1. 🫁 Global Respiratory & Infectious Health (The Lancet): The new global report on Tuberculosis highlights persistent diagnostic gaps, multidrug resistance challenges, and urgency for accelerated funding and prevention.
2. 🎗️ Precision Oncology (ESMO): Publication of the Pan-Asian adapted ESMO Clinical Practice Guidelines for Non-Small-Cell Lung Cancer (NSCLC), harmonizing western trial data with Asian clinical practice.
3. 🧬 Regenerative Medicine (Bioactive Materials): A breakthrough paradigm shift using microenvironment-reprogramming biomaterials to reverse intervertebral disc degeneration and alleviate chronic low back pain.
4. 🔬 Nanotechnology & Food Safety (Talanta): Synthesis of bimetallic FeZr-MOF nanozyme multi-channel sensors for rapid, ultra-sensitive detection of harmful pesticide residues in agricultural supplies.
5. 👵 Humanitarian Health Equity (The Lancet Healthy Longevity): Launch of the 'PARTICIPATE' framework establishing fundamental healthcare rights for older populations during humanitarian crises.

Structure strictly as follows:
English Section:
[Catchy hook introducing the weekly science roundup. Then present the 5 key breakthroughs clearly with bullet points and emojis, explaining their real-world impact. Conclude with an engaging question inviting the community to share which breakthrough they find most impactful.]

---
Arabic Section:
[نفس المحتوى بصياغة عربية علمية فصيحة، ملهمة، واحترافية تماماً، مع النقاط الخمس والتأثير العملي، وخاتمة تفاعلية.]

Ensure you literally include 'English Section:' and 'Arabic Section:' before each part, separated by '---'.
Do not add other bracketed titles.
"""

    print("🤖 Generating summary content with OpenAI (gpt-4o-mini)...")
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    ai_text = completion.choices[0].message.content.strip()
    
    hashtags = (
        "#WeeklyDigest\n"
        "#ScienceNews\n"
        "#HealthTech\n"
        "#MedicalResearch\n"
        "#Innovation\n"
        "#GlobalHealth\n"
        "#PublicHealth\n"
        "#Research"
    )
    
    full_post_content = f"🌐 **Weekly Science Digest / الحصاد العلمي الأسبوعي** 🔬\n\n{ai_text}\n\n{hashtags}"
    
    print("\n📝 Final Post Content:")
    print("=" * 60)
    print(full_post_content)
    print("=" * 60)
    
    # Post to LinkedIn
    author_key = "LINKEDIN_AUTHOR_URN"
    target_urn = os.getenv(author_key)
    print(f"\n🚀 Posting to LinkedIn ({target_urn if target_urn else 'Default Profile'})...")
    
    response, final_author = post_to_linkedin(full_post_content, author_urn=target_urn)
    
    if response and response.status_code == 201:
        post_id = response.json().get('id')
        print(f"✅ Successfully posted weekly digest to LinkedIn! Post ID: {post_id}")
        
        # Add comment with journals & references
        comment_text = (
            "📚 المصادر والدوريات العلمية المشمولة في حصاد الأسبوع / Featured Journals & Sources:\n"
            "• The Lancet (Tuberculosis & Healthy Longevity Series)\n"
            "• ESMO Open (Oncology Clinical Guidelines)\n"
            "• Bioactive Materials (Regenerative Biomaterials)\n"
            "• Talanta (Nanotechnology & Analytical Chemistry)"
        )
        post_comment(post_id, comment_text, final_author)
        
        # Save to history.json
        history_file = "history.json"
        posted_urls = []
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as hf:
                    posted_urls = json.load(hf)
            except Exception:
                posted_urls = []
                
        entry_title = "Weekly Science Digest - Global Scientific Events (Nov 11, 2026)"
        if entry_title not in posted_urls:
            posted_urls.append(entry_title)
            with open(history_file, "w") as hf:
                json.dump(posted_urls, hf)
            print("💾 Saved to history.json")
            
        return post_id
    else:
        print("❌ Failed to post weekly digest to LinkedIn.")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    main()
