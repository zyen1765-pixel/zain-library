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

# --- 4. دالة التحميل عبر الـ API (المنقذة) ---
def get_download_link(url, mode):
    # قائمة بسيرفرات Cobalt تعمل حالياً (بدائل في حال التوقف)
    # هذه السيرفرات تعمل كوسيط لتخطي حظر يوتيوب
    INSTANCES = [
        "https://api.cobalt.tools",        # السيرفر الرئيسي
        "https://cobalt.kwiatekmiki.pl",   # سيرفر بديل 1
        "https://cobalt.arms.nu",          # سيرفر بديل 2
        "https://cobalt.moshibox.org",     # سيرفر بديل 3
        "https://cobalt.wafflehacker.io"   # سيرفر بديل 4
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    # إعدادات الطلب
    payload = {
        "url": url,
        "filenamePattern": "basic"
    }
    
    if mode == "audio":
        payload["isAudioOnly"] = True
    else:
        payload["vQuality"] = "720"
        
    last_error = ""

    # تجربة السيرفرات واحداً تلو الآخر
    for base_url in INSTANCES:
        try:
            api_endpoint = f"{base_url}/api/json"
            # طلب الرابط من السيرفر
            response = requests.post(api_endpoint, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # التحقق من نجاح العملية
                if "url" in data:
                    return data["url"], None # نجحنا! أعد الرابط المباشر
                elif "status" in data and data["status"] == "error":
                    last_error = data.get("text", "Unknown error")
                    continue # جرب السيرفر التالي
            else:
                last_error = f"HTTP {response.status_code}"
                continue
                
        except Exception as e:
            last_error = str(e)
            continue
            
    return None, f"فشلت جميع المحاولات. تأكد من الرابط. ({last_error})"

# --- 5. الهيدر واللوغو ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
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

        st.markdown("<p style='color:#38bdf8; font-size:0.9rem; margin-top:10px;'>⬇️ تحميل مباشر (سريع):</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        # أزرار التحميل
        with c1:
            if st.button("🎵 تحميل صوت (MP3)", key=f"btn_mp3_{unique_key}"):
                with st.spinner("جاري جلب الرابط..."):
                    direct_link, err = get_download_link(item['path'], "audio")
                    if direct_link:
                        # هنا نعطيه الرابط المباشر للتحميل فوراً
                        st.markdown(f'<a href="{direct_link}" download="{item["title"]}.mp3" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: block; text-align: center;">💾 اضغط هنا لبدء التحميل</a>', unsafe_allow_html=True)
                    else:
                        st.error(f"خطأ: {err}")
        
        with c2:
            if st.button("📺 تحميل فيديو (MP4)", key=f"btn_vid_{unique_key}"):
                with st.spinner("جاري جلب الرابط..."):
                    direct_link, err = get_download_link(item['path'], "video")
                    if direct_link:
                        st.markdown(f'<a href="{direct_link}" download="{item["title"]}.mp4" style="background-color: #38bdf8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: block; text-align: center;">💾 اضغط هنا لبدء التحميل</a>', unsafe_allow_html=True)
                    else:
                        st.error(f"خطأ: {err}")

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
