import os
import openai
from scripts.scraper import fetch_trends
from scripts.linkedin_poster import post_to_linkedin

openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    print("جاري البحث عن قصص علمية جديدة...")
    trends = fetch_trends()
    
    if not trends:
        print("لم يتم العثور على أخبار اليوم.")
        return

    # الـ Prompt المصمم ليكون مدرس مطلع وحكواتي
    prompt = f"""
    بصفتك مدرساً واسع الاطلاع، ومبدعاً في تقريب العلوم للواقع.. 
    اكتب مقالاً لـ LinkedIn بالعربية حول هذه التطورات:
    {chr(10).join(trends)}

    الأسلوب المطلوب:
    1. ابدأ بأسلوب "حكاية" (مثلاً: تخيل لو كان جسمنا.. أو هل سألت نفسك يوماً..).
    2. بسط العلم المعقد بتشبيهات من حياتنا اليومية (مثل تشبيه الخلايا بالعمال، أو الـ AI ببوصلة ذكية).
    3. خاطب المتخصصين بعمق المعلومة، وغير المتخصصين بسلاسة المعنى.
    4. اجعل النبرة ملهمة تدعو للتفاؤل بمستقبل الصحة العامة.
    5. أضف هاشتاجات: #صحة_عامة #تكنولوجيا_صحية #مستقبل_الطب.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "أنت مدرس مطلع ومبسط للعلوم بأسلوب قصصي ملهم."},
                      {"role": "user", "content": prompt}]
        )
        article = response.choices[0].message.content
        
        print("جاري النشر على لينكد إن...")
        result = post_to_linkedin(article)
        if result.status_code in [200, 201]:
            print("تم النشر بنجاح!")
        else:
            print(f"خطأ في النشر: {result.text}")
            
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    main()
