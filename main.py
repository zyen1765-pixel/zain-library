import streamlit as st
import json
import os
import time
import base64
import yt_dlp
from PIL import Image

# --- 1. إعدادات الصفحة (يجب أن تكون في البداية دائماً) ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="💎", # سنحاول تحديثها لاحقاً إذا وجدنا اللوغو
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. تحسين السرعة (Caching) ---

# تسريع تشغيل مكتبة الصوت (يعمل مرة واحدة فقط)
@st.cache_resource
def setup_ffmpeg():
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except ImportError:
        pass

setup_ffmpeg() # استدعاء الدالة

# تسريع تحويل الصور (يحفظ النتيجة في الذاكرة)
@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    :root { --bg-dark: #0f172a; --primary: #38bdf8; --glass: rgba(30, 41, 59, 0.7); }
    .stApp { background-color: var(--bg-dark) !important; background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%); background-attachment: fixed; }

    /* تنسيق النصوص */
    h1 { font-weight: 900 !important; color: white !important; }
    h3, p, label, div, span { text-align: right; }

    /* تنسيق اللوغو الاحترافي */
    .app-icon {
        width: 100px;
        height: 100px;
        object-fit: contain;
        background-color: white;
        border-radius: 20px;
        border: 3px solid #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
        display: block; 
    }
    .app-icon:hover { transform: scale(1.05); border-color: var(--primary); }

    /* تنسيق البطاقات */
    .streamlit-expanderHeader {
        background-color: var(--glass);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        color: white !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }
    .streamlit-expanderHeader:hover { border-color: var(--primary); color: var(--primary) !important; }
    .streamlit-expanderHeader p { font-size: 1.1rem; font-weight: bold; }
    .streamlit-expanderContent { background-color: rgba(0,0,0,0.2); border-radius: 0 0 10px 10px; border: 1px solid rgba(255,255,255,0.05); border-top: none; }

    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; }
    </style>
""", unsafe_allow_html=True)

# --- 4. إدارة البيانات ---
DB_FILE = "zain_library.json"
MEDIA_FOLDER = "media"
TEMP_DOWNLOADS = "temp_downloads"

if not os.path.exists(MEDIA_FOLDER): os.makedirs(MEDIA_FOLDER)
if not os.path.exists(TEMP_DOWNLOADS): os.makedirs(TEMP_DOWNLOADS)

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
    elif "youtu.be/" in u and "?" not in u: pass 
    if "instagram.com" in u and "?" in u: u = u.split("?")[0]
    return u

# --- 5. دالة التحميل ---
def download_media(url, format_type):
    ydl_opts = {
        'outtmpl': f'{TEMP_DOWNLOADS}/%(title)s.%(ext)s',
        'quiet': True, 'no_warnings': True, 'restrictfilenames': True,
        'socket_timeout': 30,
        'ffmpeg_location': None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    if format_type == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
    elif format_type == '360':
        ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif format_type == '720':
        ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                base, _ = os.path.splitext(filename)
                filename = base + ".mp3"
            return filename, info.get('title', 'video')
    except Exception as e:
        return None, str(e)

# --- 6. الهيدر (مع اللوغو) ---

logo_path = None
possible_logos = ["1.jpg", "zain_logo.png", "static/images/zain_logo.png"]
for p in possible_logos:
    if os.path.exists(p):
        logo_path = p
        break

if logo_path:
    # سيستخدم الدالة السريعة (المحفوظة في الذاكرة)
    img_b64 = get_img_as_base64(logo_path)

    # استخدام أعمدة Streamlit
    col_logo, col_space, col_title = st.columns([0.2, 0.1, 0.7])

    with col_logo:
        # عرض اللوغو
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="app-icon">', unsafe_allow_html=True)

    with col_title:
        # عرض العنوان
        st.markdown("""
            <div style="text-align: right; padding-top: 10px;">
                <h1 style="margin: 0; font-size: 3rem; color: white;">مكتبة زين</h1>
                <p style="opacity: 0.8; font-size: 1.1rem; color: #ccc; margin: 0;">مساحتك الخاصة للإبداع</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)
    st.warning(f"⚠️ لم يتم العثور على صورة اللوغو: {possible_logos[0]}")


# --- 7. بقية الواجهة ---
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
    elif "instagram" in item['path']: icon = "📸"
    elif "tiktok" in item['path']: icon = "🎵"

    card_label = f"{icon} {item['title']}  |  📅 {item['date']}"

    with st.expander(card_label):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        elif item['type'] == 'local':
            st.video(item['path'])
        else:
            st.info(f"رابط خارجي: {item['path']}")

        if item['type'] != 'local':
            st.markdown("<p style='color:#38bdf8; font-size:0.9rem; margin-top:10px;'>⬇️ تحميل بصيغة:</p>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🎵 MP3", key=f"btn_mp3_{unique_key}"):
                    with st.spinner("جاري التحويل..."):
                        fpath, title = download_media(item['path'], 'mp3')
                        if fpath:
                            st.success("✅ جاهز")
                            with open(fpath, "rb") as file:
                                st.download_button("💾 حفظ", file, file_name=f"{title}.mp3", mime="audio/mpeg", key=f"dl_mp3_{unique_key}")
                        else: st.error("خطأ")
            with c2:
                if st.button("📺 360p", key=f"btn_360_{unique_key}"):
                    with st.spinner("جاري التحميل..."):
                        fpath, title = download_media(item['path'], '360')
                        if fpath:
                            st.success("✅ جاهز")
                            with open(fpath, "rb") as file:
                                st.download_button("💾 حفظ", file, file_name=f"{title}_360.mp4", mime="video/mp4", key=f"dl_360_{unique_key}")
            with c3:
                if st.button("HD 720p", key=f"btn_720_{unique_key}"):
                    with st.spinner("جاري التحميل..."):
                        fpath, title = download_media(item['path'], '720')
                        if fpath:
                            st.success("✅ جاهز")
                            with open(fpath, "rb") as file:
                                st.download_button("💾 حفظ", file, file_name=f"{title}_720.mp4", mime="video/mp4", key=f"dl_720_{unique_key}")

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