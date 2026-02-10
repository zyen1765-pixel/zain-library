import streamlit as st
import json
import os
import time
import base64
import requests
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. نظام الحماية ---
PASSWORD = "12345"  # كلمة السر

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True

    st.markdown("""
        <style>
        .stApp { background-color: #0f172a; color: white; }
        .stTextInput input { text-align: center; direction: ltr; color: white; background-color: #1e293b; border: 1px solid #334155; }
        h1 {text-align: center; color: white; font-family: sans-serif;}
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🔒 المكتبة محمية")
    pwd_input = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("دخول 🔓"):
        if pwd_input == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور خاطئة")
    return False

if not check_password():
    st.stop()

# --- 3. التصميم (CSS) - الإصلاح الجذري للخطوط ---
st.markdown("""
    <style>
    /* استيراد خط المراعي */
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    /* 1. إعداد الخلفية والألوان الأساسية (بدون إجبار الخط هنا) */
    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    /* 2. تطبيق خط المراعي على النصوص الصريحة *فقط* */
    h1, h2, h3, h4, h5, h6, p, label, button, input, textarea, .stMarkdown {
        font-family: 'Almarai', sans-serif !important;
    }
    
    /* 3. منع الخط عن الأيقونات والرموز (هذا يحل مشكلة arrow_right) */
    i, .material-icons, [data-testid="stExpanderToggleIcon"] {
        font-family: sans-serif !important;
    }

    /* تنسيق النصوص */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #ffffff !important;
        text-align: right;
    }

    /* حقول الإدخال */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        direction: rtl;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* --- إصلاح البطاقات (Expander) --- */
    
    /* إخفاء السهم تماماً (الحاوية والأيقونة) */
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        margin-bottom: 10px;
        display: block !important;
        position: relative;
    }

    .streamlit-expanderHeader p {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-align: right !important;
        width: 100% !important;
        padding-right: 0 !important;
    }

    .streamlit-expanderContent {
        background-color: transparent !important;
        border: none !important;
        padding: 10px 20px !important;
        text-align: right !important;
    }
    
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 1.5em 0 !important;
    }

    /* أزرار التحميل */
    .dl-link {
        display: block; width: 100%; padding: 12px; margin: 8px 0;
        text-align: center; border-radius: 8px; text-decoration: none !important;
        font-weight: 700; color: white !important; border: 1px solid rgba(255,255,255,0.2);
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    .dl-link:hover { opacity: 0.9; transform: translateY(-2px); }

    /* تنسيق اللوغو */
    .center-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 130px; 
        height: auto;
        object-fit: contain;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. إدارة الملفات ---
DB_FILE = "zain_library.json"
if 'videos' not in st.session_state:
    if os.path.exists(DB_FILE):
        try: st.session_state.videos = json.load(open(DB_FILE, "r", encoding="utf-8"))
        except: st.session_state.videos = []
    else: st.session_state.videos = []

def save_to_disk():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.videos, f, ensure_ascii=False, indent=4)

def fix_youtube_url(url):
    if not url: return ""
    u = url.strip()
    if "youtube.com/shorts/" in u:
        video_id = u.split("shorts/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={video_id}"
    elif "youtu.be/" in u:
        video_id = u.split("youtu.be/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={video_id}"
    if "instagram.com" in u: u = u.split("?")[0]
    return u

def get_youtube_title(url):
    try:
        clean_url = fix_youtube_url(url)
        oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            return response.json().get('title')
    except: pass
    return None

# --- 5. الهيدر (اللوغو الجديد) ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return None

# نبحث عن اللوغو الجديد أولاً
logo_file = None
if os.path.exists("zain_logo_new.png"): logo_file = "zain_logo_new.png"
elif os.path.exists("zain_logo.png"): logo_file = "zain_logo.png"

if logo_file:
    img_b64 = get_img_as_base64(logo_file)
    st.markdown(f"""
        <div style="text-align: center; padding-top: 20px;">
            <img src="data:image/png;base64,{img_b64}" class="center-logo">
            <h1 style="margin-top: 15px; font-size: 3rem; color: white; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">مكتبة زين</h1>
            <p style="opacity: 0.9; font-size: 1.2rem; color: #e2e8f0; margin: 5px 0 30px 0; font-weight: 300;">مساحتك الخاصة للإبداع</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)

# --- 6. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو")
    if st.button("🔍 جلب العنوان"):
        if url_in:
            fetched_title = get_youtube_title(url_in)
            if fetched_title:
                st.session_state.temp_title = fetched_title
                st.success("تم!")
            else: st.warning("اكتب العنوان يدوياً")
    
    default_title = st.session_state.get('temp_title', '')
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان", value=default_title)
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ ✅"):
        if title_in and url_in:
            final_url = fix_youtube_url(url_in)
            st.session_state.videos.append({"title": title_in, "path": final_url, "category": cat_in, "type": "url", "date": time.strftime("%Y-%m-%d")})
            save_to_disk()
            if 'temp_title' in st.session_state: del st.session_state.temp_title
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

def show_expander_card(item, idx, cat_name):
    unique_key = f"{cat_name}_{idx}"
    label = f"📂 {item['title']} | 📅 {item['date']}"
    
    with st.expander(label):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("---")
        st.write("##### 1️⃣ انسخ الرابط:")
        st_copy_to_clipboard(item['path'], "📋 نسخ", key=f"copy_{unique_key}")
        
        st.write("##### 2️⃣ التحميل:")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt (شورتس)</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("حذف 🗑️", key=f"del_{unique_key}"):
            st.session_state.videos.remove(item)
            save_to_disk()
            st.rerun()

for i, cat in enumerate(categories):
    with tabs[i]:
        items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        if not items: st.info("لا يوجد محتوى")
        for idx, vid in enumerate(items):
            show_expander_card(vid, idx, cat)
