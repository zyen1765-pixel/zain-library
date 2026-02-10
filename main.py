import streamlit as st
import os
import json
import time
import base64
import requests
import shutil
import yt_dlp
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
    /* تحسين شكل زر تحميل الملف */
    .stFileUploader { text-align: right; }
    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; }
    </style>
""", unsafe_allow_html=True)

# --- 3. إدارة الملفات ---
DB_FILE = "zain_library.json"
TEMP_DIR = "/tmp/zain_downloads"
COOKIES_FILE = "/tmp/cookies.txt" # مسار ملف الكوكيز المؤقت

if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR, exist_ok=True)

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

# --- 4. دالة التحميل عبر API (الخيار الأول - الأسهل) ---
def download_via_cobalt(url, mode):
    # قائمة سيرفرات محدثة وقوية
    SERVERS = [
        "https://cobalt.moshibox.org",
        "https://cobalt.arms.nu",
        "https://cobalt.ethan.eu.org",
        "https://cobalt.rudart.com",
        "https://cobalt.wafflehacker.io",
        "https://api.cobalt.tools", 
        "https://cobalt.kwiatekmiki.pl"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    data = {"url": url, "filenamePattern": "basic"}
    if mode == "audio": data["isAudioOnly"] = True
    
    last_err = ""
    for base in SERVERS:
        try:
            # نجرب الاتصال بالسيرفر
            resp = requests.post(f"{base}/api/json", json=data, headers=headers, timeout=8)
            if resp.status_code == 200:
                json_resp = resp.json()
                if "url" in json_resp:
                    # التحميل من الرابط الناتج
                    file_resp = requests.get(json_resp["url"], stream=True, timeout=20)
                    return file_resp.content, None, base # إرجاع المحتوى والسيرفر الناجح
        except Exception as e:
            last_err = str(e)
            continue
            
    return None, f"فشلت جميع السيرفرات. (آخر خطأ: {last_err})", None

# --- 5. دالة التحميل عبر yt-dlp (الخيار الثاني - الكوكيز) ---
def download_via_ytdlp(url, mode, cookie_path=None):
    try:
        # تنظيف المجلد
        if os.path.exists(TEMP_DIR): shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        opts = {
            'outtmpl': f'{TEMP_DIR}/%(title)s.%(ext)s',
            'quiet': True, 'no_warnings': True, 'restrictfilenames': True,
        }
        
        # إذا رفع المستخدم ملف كوكيز، نستخدمه (هذا يحل مشكلة الحظر 100%)
        if cookie_path and os.path.exists(cookie_path):
            opts['cookiefile'] = cookie_path
        
        if mode == "audio":
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]
        else:
            opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            fname = ydl.prepare_filename(info)
            if mode == "audio": fname = os.path.splitext(fname)[0] + ".mp3"
            return fname, info.get('title', 'media'), None
            
    except Exception as e:
        return None, None, str(e)

# --- 6. الهيدر ---
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

# --- 7. الشريط الجانبي (المفتاح الذهبي) ---
with st.sidebar:
    st.header("⚙️ إعدادات متقدمة")
    st.info("إذا واجهت مشاكل في التحميل، يمكنك رفع ملف Cookies هنا لحل مشكلة حظر يوتيوب.")
    uploaded_cookies = st.file_uploader("ارفع ملف cookies.txt (اختياري)", type="txt")
    
    cookie_used = False
    if uploaded_cookies is not None:
        with open(COOKIES_FILE, "wb") as f:
            f.write(uploaded_cookies.getbuffer())
        st.success("✅ تم تفعيل الكوكيز!")
        cookie_used = True

# --- 8. الواجهة الرئيسية ---
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

def handle_download(item, mode, unique_key):
    # محاولة 1: السيرفرات الخارجية (Cobalt)
    with st.spinner("جاري محاولة التحميل عبر السيرفرات السحابية..."):
        content, err, srv = download_via_cobalt(item['path'], mode)
        if content:
            ext = "mp3" if mode == "audio" else "mp4"
            st.success(f"تم التحميل من السيرفر: {srv}")
            st.download_button(f"💾 حفظ {ext.upper()}", content, file_name=f"{item['title']}.{ext}", mime=f"audio/{ext}" if mode=="audio" else "video/mp4", key=f"dl_api_{unique_key}")
            return

    # محاولة 2: التحميل المباشر (yt-dlp) إذا فشلت السيرفرات
    st.warning(f"فشلت السيرفرات السحابية: {err}")
    with st.spinner("جاري المحاولة عبر المحرك الداخلي (yt-dlp)..."):
        # استخدام ملف الكوكيز إذا تم رفعه
        c_path = COOKIES_FILE if cookie_used else None
        fpath, title, err_local = download_via_ytdlp(item['path'], mode, c_path)
        
        if fpath and os.path.exists(fpath):
            with open(fpath, "rb") as file:
                ext = "mp3" if mode == "audio" else "mp4"
                st.success("✅ تم التحميل بنجاح عبر المحرك الداخلي")
                st.download_button(f"💾 حفظ {ext.upper()}", file, file_name=f"{title}.{ext}", mime=f"audio/{ext}" if mode=="audio" else "video/mp4", key=f"dl_loc_{unique_key}")
        else:
            st.error(f"❌ فشل التحميل نهائياً. السبب: {err_local}")
            if "Sign in" in str(err_local) or "403" in str(err_local):
                st.info("💡 الحل: يوتيوب يحظر السيرفر. قم بتحميل ملف cookies.txt من متصفحك وارفعه في القائمة الجانبية.")

def show_expander_card(item, idx, cat_name):
    unique_key = f"{cat_name}_{idx}"
    icon = "🎥"
    if item['type'] == 'local': icon = "📂"
    
    with st.expander(f"{icon} {item['title']}  |  📅 {item['date']}"):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("<p style='color:#38bdf8; font-size:0.9rem; margin-top:10px;'>⬇️ خيارات التحميل:</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            if st.button("🎵 تحميل صوت (MP3)", key=f"btn_mp3_{unique_key}"):
                handle_download(item, "audio", unique_key)
        
        with c2:
            if st.button("📺 تحميل فيديو (MP4)", key=f"btn_vid_{unique_key}"):
                handle_download(item, "video", unique_key)

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
