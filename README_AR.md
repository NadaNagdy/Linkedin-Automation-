# LinkedIn Organization Post Fixer 🔧

## المشكلة
السكريبت بتاعك بينشر بنجاح على البروفايل الشخصي، بس بيفشل في النشر على صفحة الشركة بسبب:
- خطأ `403 ACCESS_DENIED`
- مشكلة في `/author` field
- احتمال الـ Organization ID مش صحيح

## الحل
السكريبت ده هيساعدك:
1. ✅ يجيب كل الـ Organizations اللي عندك صلاحيات عليها
2. ✅ يجرّب ينشر على كل واحدة فيهم
3. ✅ يديكي الـ Organization ID الصحيح

---

## التحضير

### 1️⃣ تنصيب المكتبات المطلوبة
```bash
pip install requests python-dotenv
```

### 2️⃣ إعداد ملف `.env`
انسخي ملف `.env.example` لـ `.env`:
```bash
cp .env.example .env
```

### 3️⃣ حطّي الـ Access Token
افتحي ملف `.env` وحطّي الـ Access Token بتاعك:
```
LINKEDIN_ACCESS_TOKEN=AQV8aBc...your_actual_token_here...XYZ
```

**ملاحظة:** الـ Access Token تقدري تجيبيه من:
- الـ OAuth flow اللي بتستخدميه حالياً
- أو من LinkedIn Developer Portal → Your App → Auth tab

---

## التشغيل

```bash
python linkedin_org_fix.py
```

---

## النتيجة المتوقعة

السكريبت هيعرض:

```
🔍 بجلب الـ Organizations اللي عندك صلاحيات عليها...

============================================================
✅ الشركات اللي عندك صلاحيات Admin عليها:
============================================================

📌 اسم الشركة: Your Company Name
   Organization ID: 12345678
   Vanity Name: your-company
   الصلاحية: ADMINISTRATOR
   الحالة: APPROVED

============================================================
🚀 بجرّب أنشر post على: Your Company Name
   Organization ID: 12345678
============================================================

📤 بعمل POST request...

✅ نجح! تم النشر على صفحة الشركة بنجاح! 🎉

Post ID: urn:li:share:7425867271660728320
```

---

## الخطوة التالية

بعد ما السكريبت ينجح، هتلاقي الـ **Organization ID الصحيح**.

استخدميه في السكريبت الأساسي بتاعك بدل `111716442`:

```python
# قبل كده (غلط)
"author": f"urn:li:organization:111716442"

# بعد كده (صح)
"author": f"urn:li:organization:12345678"  # الرقم اللي طلع معاكي
```

---

## استكشاف الأخطاء

### لو ظهر خطأ `401 Unauthorized`:
- تأكدي إن الـ Access Token صحيح ومتنفذش
- جرّبي تعملي refresh للـ token

### لو ظهر خطأ `403 Forbidden`:
- تأكدي إن حسابك فعلاً Super Admin على الشركة
- تأكدي إن الـ App عندها `w_organization_social` permission

### لو مفيش organizations ظهرت:
- ممكن يكون الـ API endpoint محتاج permissions تانية
- جرّبي تعملي request manual من LinkedIn Developer Portal

---

## معلومات تقنية

### LinkedIn API Version
السكريبت بيستخدم:
- API Version: `202406`
- Protocol Version: `2.0.0`
- Endpoint: `v2/ugcPosts`

### الـ Author Format الصحيح
```json
{
  "author": "urn:li:organization:ORG_ID"
}
```

❌ **غلط:** `urn:li:person:PERSON_URN`  
✅ **صح:** `urn:li:organization:ORG_ID`

---

## أسئلة؟

لو عندك أي مشكلة أو محتاجة مساعدة، قوليلي! 😊

---

**Created by:** Claude  
**Date:** 2026-02-07
