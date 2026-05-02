import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# تفعيل الـ CORS حتى يگدر الموقع يحچي ويا السيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

@app.post("/get-info")
async def get_video_info(request: DownloadRequest):
    url = request.url
    
    if not url:
        raise HTTPException(status_code=400, detail="وين الرابط حمودي؟")

    # إعدادات المكتبة لجلب المعلومات فقط بدون تحميل الملف للسيرفر
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats_list = []
            
            # إذا كان الرابط يحتوي على قائمة (مثل بوست انستا بيه صور وفيديو)
            entries = info.get('entries', [info])
            
            all_media = []
            for entry in entries:
                media_data = {
                    "title": entry.get('title', 'No Title'),
                    "thumbnail": entry.get('thumbnail'),
                    "formats": []
                }
                
                for f in entry.get('formats', []):
                    # نفلتر الروابط المباشرة اللي تشتغل (فيديو + صوت)
                    if f.get('url') and (f.get('vcodec') != 'none' or f.get('ext') == 'mp4'):
                        media_data["formats"].append({
                            'quality': f.get('format_note') or f.get('resolution') or 'Normal',
                            'ext': f.get('ext'),
                            'url': f.get('url'),
                            'size': f.get('filesize_approx') or f.get('filesize')
                        })
                
                # إضافة خيار "صوت فقط" إذا جان يوتيوب
                audio_only = [f.get('url') for f in entry.get('formats', []) if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
                if audio_only:
                    media_data["audio_url"] = audio_only[0]
                
                all_media.append(media_data)

            return {
                "success": True,
                "data": all_media
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # هذا البورت اللي راح يشتغل عليه السيرفر محلياً أو على ريندر
    uvicorn.run(app, host="0.0.0.0", port=7860)
