import os
from openai import OpenAI
from scripts.scraper import fetch_trends
from scripts.linkedin_poster import post_to_linkedin

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    print("🚀 جاري بدء رحلة البحث عن جديد الصحة...")
    trends = fetch_trends()
    
    if not trends:
        print("📭 لا يوجد أخبار جديدة اليوم.")
        return

    prompt = f"""
    أنت مدرس مطلع ومبسط للعلوم. اكتب مقال LinkedIn بالعربية عن:
    {chr(10).join(trends)}

    الأسلوب:
    - ابدأ بحكاية مشوقة أو تساؤل ذكي.
    - استخدم تشبيهات من حياتنا اليومية (مثل تشبيه المناعة ببرنامج مكافحة فيروسات).
    - وازن بين العمق العلمي والبساطة.
    - النهاية ملهمة مع هاشتاجات #صحة_عامة #HealthTech.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مدرس حكواتي خبير في تبسيط العلوم."},
                      {"role": "user", "content": prompt}]
        )
        article = response.choices[0].message.content
        
        print("📤 جاري النشر على لينكد إن...")
        result = post_to_linkedin(article)
        if result and result.status_code in [200, 201]:
            print("✅ تم النشر بنجاح!")
        else:
            print(f"⚠️ فشل النشر: {result.text if result else 'لا يوجد رد'}")
            
    except Exception as e:
        print(f"💥 حدث خطأ: {e}")

if __name__ == "__main__":
    main()
