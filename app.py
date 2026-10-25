# ════════════════════════════════════════════════════════════
#  المحاضرة ٢٣ · هيكل المشروع
# ════════════════════════════════════════════════════════════
import os
import time
import logging
import re

from fastapi import FastAPI, HTTPException, Request, Response

app = FastAPI(title="Project", version="1.0")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("project")

بدأت_الخدمة = time.time()
عدادات = {
    "requests_total": 0, 
    "errors_total": 0,
    "latency_ms_sum": 0.0, 
    "latency_ms_max": 0.0
}
حسب_المسار = {}

API_KEY = os.environ.get("MODEL_API_KEY", "")


# ════════════════════════════════════════════════════════════
#  ⟵⟵⟵  شغلك هون  ⟶⟶⟶
# ════════════════════════════════════════════════════════════

المعرفة = {
    "منيو": (
        "قائمة المشروبات والحلويات:\n"
        "• إسباريصو / لاتيه / كابتشينو / V60\n"
        "• ماتشا وايس ماتشا لاتيه\n"
        "• تشيز كيك، كيكة الشوكولاتة، وكرواسون طازج يومياً.",
        ["قائمة الطعام والشراب · قائمة 2026"]
    ),
    "مشروب": (
        "أشهر مشروباتنا: أيس لاتيه بالكراميل المملح، كولد برو، والماتشا اليابانية.",
        ["قائمة الطعام والشراب · قسم المشروبات"]
    ),
    "دوام": (
        "نستقبلكم يومياً من الساعة ٧:٠٠ صباحاً حتى ١١:٣٠ مساءً (الجمعة من ١:٠٠ ظهراً).",
        ["معلومات الفرع · صفحة 1"]
    ),
    "ساعات": (
        "نستقبلكم يومياً من الساعة ٧:٠٠ صباحاً حتى ١١:٣٠ مساءً (الجمعة من ١:٠٠ ظهراً).",
        ["معلومات الفرع · صفحة 1"]
    ),
    "عنوان": (
        "فرعنا الرئيسي: شارع الملك عبد الله، مقابل بوليفارد العبدلي، عمان.",
        ["دليل الموقع · خريطة الفروع"]
    ),
    "موقع": (
        "فرعنا الرئيسي: شارع الملك عبد الله، مقابل بوليفارد العبدلي، عمان.",
        ["دليل الموقع · خريطة الفروع"]
    ),
    "توصيل": (
        "يمكنك الطلب عبر تطبيقات التوصيل: طلبات (Talabat)، جاهز (Jahez)، أو هنقرستيشن.",
        ["دليل الخدمات · التوصيل الخارجي"]
    ),
    "عرض": (
        "عرض السعادة يومياً من ٨ لـ ١٠ صباحاً: قهوتك اليومية + كرواسون بـ ٢.٥ دينار فقط!",
        ["عروض المقهى · صفحة العروض الشهرية"]
    ),
    "واي فاي": (
        "يتوفر إنترنت مجاني وسريع للزبناء والدارسين، مع توفر مقابس كهرباء في معظم الطاولات.",
        ["الخدمات المتاحة · صفحة 3"]
    ),
    "انترنت": (
        "يتوفر إنترنت مجاني وسريع للزبناء والدارسين، مع توفر مقابس كهرباء في معظم الطاولات.",
        ["الخدمات المتاحة · صفحة 3"]
    ),
}

def طبّع(س: str) -> str:
    س = re.sub(r"[أإآ]", "ا", س)
    س = س.replace("ة", "ه").replace("ى", "ي")
    س = re.sub(r"[ً-ْ]", "", س)
    return " ".join(س.split()).lower()

def جاوب(سؤال: str):
    """بتاخد سؤال · بترجّع (جواب, مصادر)."""
    س_منظف = سؤال.strip()
    if not س_منظف:
        return "", []

    for مفتاح, (جواب, مصادر) in المعرفة.items():
        if طبّع(مفتاح) in س_منظف:
            return جواب, مصادر

    return "", []


# ════════════════════════════════════════════════════════════
#  ⟵⟵⟵  نهاية شغلك · تحت ما بتلمس إشي  ⟶⟶⟶
# ════════════════════════════════════════════════════════════


@app.middleware("http")
async def قيس_كل_طلب(request: Request, call_next):
    بلّش = time.perf_counter()
    رد = await call_next(request)
    مدة = (time.perf_counter() - بلّش) * 1000

    عدادات["requests_total"] += 1
    عدادات["latency_ms_sum"] += مدة
    if مدة > عدادات["latency_ms_max"]:
        عدادات["latency_ms_max"] = مدة
    if رد.status_code >= 400:
        عدادات["errors_total"] += 1

    مسار = request.url.path
    حسب_المسار[مسار] = حسب_المسار.get(مسار, 0) + 1

    مستوى = logging.WARNING if رد.status_code >= 400 else logging.INFO
    log.log(مستوى, "path=%s | status=%s | ms=%.1f",
            مسار, رد.status_code, مدة)
    return رد


@app.get("/")
def home():
    """صفحة الترحيب."""
    return {
        "service": app.title,
        "status": "running",
        "endpoints": ["/ask?q=سؤالك", "/health", "/metrics", "/docs"],
    }


@app.get("/ask")
def ask(q: str):
    """السؤال الرئيسي · وهاد اللي بيفحصه الفاحص."""
    جواب, مصادر = جاوب(q)
    if not جواب:
        raise HTTPException(status_code=404, detail={
            "message": f"ما لقيت جواب لـ: {q}",
            "suggestions": list(المعرفة.keys())[:5],
        })
    return {"question": q, "answer": جواب, "sources": مصادر}


@app.get("/health")
def health(response: Response):
    """فحص صحّة بيفحص فعلاً."""
    فحوصات = {
        "knowledge_loaded": len(المعرفة) > 0,
        "can_answer": bool(جاوب(next(iter(المعرفة), ""))[0])
                      if المعرفة else False,
    }
    سليمة = all(فحوصات.values())
    if not سليمة:
        response.status_code = 503
    return {"status": "ok" if سليمة else "unhealthy",
            "checks": فحوصات,
            "key_loaded": bool(API_KEY)}


@app.get("/metrics")
def metrics():
    """أرقام خدمتك."""
    ن = عدادات["requests_total"]
    return {
        "uptime_seconds": round(time.time() - بدأت_الخدمة, 1),
        "requests_total": ن,
        "errors_total": عدادات["errors_total"],
        "latency_ms_avg": round(عدادات["latency_ms_sum"] / ن, 2) if ن else 0,
        "latency_ms_max": round(عدادات["latency_ms_max"], 2),
        "by_path": dict(حسب_المسار),
    }
