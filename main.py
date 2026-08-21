import os
import json
import requests
from datetime import datetime, timedelta
from hijri_converter import Gregorian

def get_hijri_date(offset=0):
    today = datetime.now() + timedelta(days=offset)
    hijri_date = Gregorian(today.year, today.month, today.day).to_hijri()
    return hijri_date.day, hijri_date.month, hijri_date.year

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    return response.json()

def main():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    offset_str = os.environ.get("HIJRI_OFFSET", "0")

    try:
        offset = int(offset_str)
    except ValueError:
        offset = 0

    if not bot_token or not chat_id:
        print("خطأ: لم يتم العثور على المفاتيح السرية TELEGRAM_BOT_TOKEN أو TELEGRAM_CHAT_ID")
        return

    occasions_file = "occasions.json"
    if not os.path.exists(occasions_file):
        print(f"خطأ: الملف {occasions_file} غير موجود!")
        return

    with open(occasions_file, "r", encoding="utf-8") as f:
        occasions = json.load(f)

    day, month, year = get_hijri_date(offset)

    hijri_months_names = [
        "محرم الحرام", "صفر الخير", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الآخرة", "رجب الأصب", "شعبان المعظم",
        "شهر رمضان المبارك", "شوال المكرم", "ذو القعدة الحرام", "ذو الحجة الحرام"
    ]
    month_title = hijri_months_names[month - 1]

    matched_occasion = None
    for occ in occasions:
        if occ.get("day") == day and occ.get("month") == month:
            matched_occasion = occ
            break

    date_header = f"🌙 <b>مناسبات اليوم الهجري</b>\n🗓 <b>التاريخ:</b> {day} {month_title} {year} هـ"

    if matched_occasion:
        occ_type = matched_occasion.get("type", "مناسبة")
        title = matched_occasion.get("title", "")
        desc = matched_occasion.get("description", "")
        hadith = matched_occasion.get("hadith", "")

        if occ_type == "فرح":
            icon = "🎉"
            type_label = "مناسبة مباركة ولائية"
        else:
            icon = "🏴"
            type_label = "استذكار وحزن"

        message = (
            f"{date_header}\n\n"
            f"{icon} <b>{type_label}:</b>\n"
            f"✨ <b>{title}</b>\n\n"
            f"📖 <b>نبذة عن المناسبة:</b>\n{desc}\n\n"
        )

        if hadith:
            message += f"📜 <b>رواية مباركة:</b>\n<i>«{hadith}»</i>\n\n"

        message += (
            f"ــــــــــــــــــــــــــــــــــــــــ\n"
            f"🔗 <b>لمتابعة السجل الكامل عبر موقعنا:</b>\n"
            f"https://y313a.github.io"
        )
    else:
        message = (
            f"{date_header}\n\n"
            f"✨ لا توجد مناسبة رئيسية مسجلة في هذا اليوم المبارك.\n\n"
            f"نسأل الله تعالى أن يجعله يوماً مباركاً وعامراً بالطاعات والسعادة عليكم."
        )

    result = send_telegram_message(bot_token, chat_id, message)
    if result.get("ok"):
        print("تم إرسال الرسالة بنجاح إلى القناة!")
    else:
        print(f"فشل إرسال الرسالة: {result}")

if __name__ == "__main__":
    main()
