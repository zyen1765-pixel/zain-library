import streamlit as st
import os
import time
import base64
import subprocess # لتشغيل ffmpeg
from pytubefix import YouTube # المكتبة الجديدة
from PIL import Image

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. دوال مساعدة ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# --- 3. التصميم (CSS) ---
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

# --- 4. إعداد المجلدات ---
DB_FILE = "zain_library.json"
TEMP_DOWNLOADS = "/tmp/zain_downloads" # استخدام مجلد المؤقتات في السيرفر

if not os.path.exists(TEMP_DOWNLOADS): os.makedirs(TEMP_DOWNLOADS)
import json
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

# --- 5. دالة التحميل الجديدة (pytubefix) ---
def download_media(url, format_type):
    try:
        yt = YouTube(url, use_po_token=True) # تفعيل خاصية تجاوز الحظر
        title = yt.title
        
        # تنظيف الاسم من الرموز الممنوعة
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        
        output_path = f"{TEMP_DOWNLOADS}/{safe_title}"

        if format_type == 'mp3':
            # تحميل الصوت فقط
            stream = yt.streams.get_audio_only()
            downloaded_file = stream.download(output_path=TEMP_DOWNLOADS, filename=f"{safe_title}_raw.m4a")
            
            # تحويل إلى MP3 باستخدام FFmpeg (لضمان عمله على كل الأجهزة)
            mp3_file = f"{TEMP_DOWNLOADS}/{safe_title}.mp3"
            # أمر التحويل
            subprocess.run([
                'ffmpeg', '-i', downloaded_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', mp3_file, '-y'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return mp3_file, title, None

        elif format_type == '360':
            stream = yt.streams.filter(res="360p", file_extension='mp4', progressive=True).first()
            if not stream: # محاولة بديلة
                stream = yt.streams.filter(res="360p").first()
            final_file = stream.download(output_path=TEMP_DOWNLOADS, filename=f"{safe_title}_360.mp4")
            return final_file, title, None
            
        elif format_type == '720':
            stream = yt.streams.filter(res="720p", file_extension='mp4', progressive=True).first()
            if not stream:
                stream = yt.streams.filter(res="720p").first()
            final_file = stream.download(output_path=TEMP_DOWNLOADS, filename=f"{safe_title}_720.mp4")
            return final_file, title, None

    except Exception as e:
        return None, None, str(e)

# --- 6. الهيدر ---
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

# --- 7. الواجهة ---
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
        # عرض الفيديو
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("<p style='color:#38bdf8; font-size:0.9rem; margin-top:10px;'>⬇️ تحميل بصيغة:</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        
        with c1:
            if st.button("🎵 MP3", key=f"btn_mp3_{unique_key}"):
                with st.spinner("جاري التحضير..."):
                    fpath, title, err = download_media(item['path'], 'mp3')
                    if fpath:
                        with open(fpath, "rb") as file:
                            st.download_button("💾 حفظ MP3", file, file_name=f"{title}.mp3", mime="audio/mpeg", key=f"dl_mp3_{unique_key}")
                    else: st.error(f"خطأ: {err}")
        
        with c2:
            if st.button("📺 360p", key=f"btn_360_{unique_key}"):
                with st.spinner("جاري التحميل..."):
                    fpath, title, err = download_media(item['path'], '360')
                    if fpath:
                        with open(fpath, "rb") as file:
                            st.download_button("💾 حفظ 360p", file, file_name=f"{title}.mp4", mime="video/mp4", key=f"dl_360_{unique_key}")
                    else: st.error(f"خطأ: {err}")

        with c3:
            if st.button("HD 720p", key=f"btn_720_{unique_key}"):
                with st.spinner("جاري التحميل..."):
                    fpath, title, err = download_media(item['path'], '720')
                    if fpath:
                        with open(fpath, "rb") as file:
                            st.download_button("💾 حفظ 720p", file, file_name=f"{title}.mp4", mime="video/mp4", key=f"dl_720_{unique_key}")
                    else: st.error(f"خطأ: {err}")

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
