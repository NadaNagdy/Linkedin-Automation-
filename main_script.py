import os
from openai import OpenAI
from scripts.scraper import fetch_trends
from scripts.linkedin_poster import post_to_linkedin
import requests

# إعداد العميل
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_my_urn(token):
    """وظيفة لاستخراج الـ URN تلقائياً إذا لم يكن موجوداً"""
    res = requests.get("https://api.linkedin.com/v2/me", headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 200:
        return res.json().get('id')
    return None

def main():
    token = os.getenv("LINKEDIN_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")

    # إذا كان الـ URN ناقص، نحاول نجيبه بالـ Token
    if not person_urn and token:
        print("🔍 الـ URN غير موجود، جاري محاولة استخراجه...")
        person_urn = get_my_urn(token)
        if person_urn:
            print(f"✅ تم العثور على الـ URN الخاص بك: {person_urn}")
            print("💡 نصيحة: ضيف الرقم ده في GitHub Secrets باسم LINKEDIN_PERSON_URN عشان توفر وقت.")
        else:
            print("❌ فشل استخراج الـ URN، تأكد من صلاحية الـ Token.")
            return

    print("📖 جاري البحث عن قصص علمية جديدة...")
    trends = fetch_trends()
    
    if not trends:
        print("📭 لم يتم العثور على أخبار جديدة اليوم.")
        return

    prompt = f"""
    بصفتك مدرساً مطلعاً وحكواتي بارع، اكتب مقالاً لـ LinkedIn بالعربية يبسط هذه العلوم:
    {chr(10).join(trends)}

    الأسلوب: حكاية ملهمة، تشبيهات من الواقع، لغة تجمع بين المتخصص وغير المتخصص، ونبرة متفائلة.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مدرس مطلع ومبسط للعلوم بأسلوب قصصي ملهم."},
                {"role": "user", "content": prompt}
            ]
        )
        article = response.choices[0].message.content
        
        print("📤 جاري النشر على لينكد إن...")
        # نمرر الـ person_urn للوظيفة
        os.environ["LINKEDIN_PERSON_URN"] = person_urn 
        result = post_to_linkedin(article)
        
        if result is not None and result.status_code in [200, 201]:
            print("🚀 تم النشر بنجاح على بروفايلك!")
        else:
            print(f"⚠️ فشل النشر: {result.text if result else 'No Response'}")
            
    except Exception as e:
        print(f"💥 حدث خطأ: {e}")

if __name__ == "__main__":
    main()
