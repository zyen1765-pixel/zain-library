import streamlit as st
import os
import json
import time
import base64
import requests
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    :root { --bg-dark: #0f172a; --primary: #38bdf8; --glass: rgba(30, 41, 59, 0.7); }
    .stApp { background-color: var(--bg-dark) !important; background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%); background-attachment: fixed; }
    h1 { font-weight: 900 !important; color: white !important; }
    h3, p, label, div, span { text-align: right; }
    .app-icon {
        width: 100px; height: 100px; object-fit: contain; background-color: white;
        border-radius: 20px; border: 3px solid #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        display: block; 
    }
    .streamlit-expanderHeader {
        background-color: var(--glass); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
        color: white !important; direction: rtl;
    }
    .streamlit-expanderContent { background-color: rgba(0,0,0,0.2); border-radius: 0 0 10px 10px; border-top: none; }
    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; }
    </style>
""", unsafe_allow_html=True)

# --- 3. إدارة الملفات ---
DB_FILE = "zain_library.json"
if 'videos' not in st.session_state:
    if os.path.exists(DB_FILE):
        try: st.session_state.videos = json.load(open(DB_FILE, "r", encoding="utf-8"))
        except: st.session_state.videos = []
    else: st.session_state.videos = []

def save_to_disk():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.videos, f, ensure_ascii=False, indent=4)

def clean_url(url):
    if not url: return ""
    u = url.strip()
    if "youtube.com/shorts/" in u: u = u.replace("shorts/", "watch?v=")
    if "instagram.com" in u: u = u.split("?")[0]
    return u

# --- 4. دالة التحميل الذكية (متعددة السيرفرات) ---
def download_media_via_api(url, mode):
    # قائمة سيرفرات بديلة (إذا تعطل واحد يعمل الآخر)
    COBALT_INSTANCES = [
        "https://api.cobalt.tools",
        "https://cobalt.kwiatekmiki.pl",
        "https://cobalt.mywaifu.best",
        "https://cobalt.q11.ba"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.0.0 Safari/537.36"
    }

    data = {
        "url": url,
        "vQuality": "720" if mode == "video" else "max",
        "filenamePattern": "basic"
    }
    
    if mode == "audio":
        data["isAudioOnly"] = True
    
    last_error = ""
    
    # حلقة تكرار تجرب السيرفرات واحداً تلو الآخر
    for base_url in COBALT_INSTANCES:
        api_url = f"{base_url}/api/json"
        try:
            # محاولة الاتصال بالسيرفر الحالي
            response = requests.post(api_url, json=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                resp_json = response.json()
                if "url" in resp_json:
                    # نجحنا! وجدنا رابط التحميل
                    download_link = resp_json["url"]
                    file_response = requests.get(download_link, stream=True)
                    
                    # تحديد الامتداد
                    ext = "mp3" if mode == "audio" else "mp4"
                    # إرجاع الملف فوراً
                    return file_response.content, None
            
        except Exception as e:
            last_error = str(e)
            continue # انتقل للسيرفر التالي في القائمة
            
    return None, f"عذراً، جميع السيرفرات مشغولة حالياً. حاول بعد قليل. (Error: {last_error})"

# --- 5. الهيدر واللوغو ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

logo_path = "zain_logo.png"
if os.path.exists(logo_path):
    img_b64 = get_img_as_base64(logo_path)
    col_logo, col_space, col_title = st.columns([0.2, 0.1, 0.7])
    with col_logo:
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="app-icon">', unsafe_allow_html=True)
    with col_title:
        st.markdown("""
            <div style="text-align: right; padding-top: 10px;">
                <h1 style="margin: 0; font-size: 3rem; color: white;">مكتبة زين</h1>
                <p style="opacity: 0.8; font-size: 1.1rem; color: #ccc; margin: 0;">مساحتك الخاصة للإبداع</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)

# --- 6. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان")
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    url_in = st.text_input("رابط الفيديو")
    if st.button("حفظ ✅"):
        if title_in and url_in:
            final_url = clean_url(url_in)
            st.session_state.videos.append({"title": title_in, "path": final_url, "category": cat_in, "type": "url", "date": time.strftime("%Y-%m-%d")})
            save_to_disk()
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

def show_expander_card(item, idx, cat_name):
    unique_key = f"{cat_name}_{idx}"
    icon = "🎥"
    if item['type'] == 'local': icon = "📂"
    
    with st.expander(f"{icon} {item['title']}  |  📅 {item['date']}"):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("<p style='color:#38bdf8; font-size:0.9rem; margin-top:10px;'>⬇️ تحميل بصيغة:</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            if st.button("🎵 تحميل صوت (MP3)", key=f"btn_mp3_{unique_key}"):
                with st.spinner("جاري الاتصال بأفضل سيرفر متاح..."):
                    file_content, err = download_media_via_api(item['path'], "audio")
                    if file_content:
                        st.download_button("💾 اضغط للحفظ", file_content, file_name=f"{item['title']}.mp3", mime="audio/mpeg", key=f"dl_mp3_{unique_key}")
                    else:
                        st.error(f"{err}")
        
        with c2:
            if st.button("📺 تحميل فيديو (MP4)", key=f"btn_vid_{unique_key}"):
                with st.spinner("جاري الاتصال بأفضل سيرفر متاح..."):
                    file_content, err = download_media_via_api(item['path'], "video")
                    if file_content:
                        st.download_button("💾 اضغط للحفظ", file_content, file_name=f"{item['title']}.mp4", mime="video/mp4", key=f"dl_vid_{unique_key}")
                    else:
                        st.error(f"{err}")

        st.markdown("---")
        if st.button("حذف الفيديو 🗑️", key=f"del_{unique_key}"):
            st.session_state.videos.remove(item)
            save_to_disk()
            st.rerun()

for i, cat in enumerate(categories):
    with tabs[i]:
        items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        if not items: st.info("لا يوجد محتوى")
        for idx, vid in enumerate(items):
            show_expander_card(vid, idx, cat)
