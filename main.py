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
PASSWORD = "12345" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True

    st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; color: white !important; }
        .stTextInput input { text-align: center; color: white !important; background-color: #1e293b !important; border: 1px solid #334155 !important; }
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

# --- 3. التصميم (CSS) - النسخة المصححة كلياً ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@400;700&display=swap');

    /* 1. الأساسيات */
    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        color: #ffffff !important;
        font-family: 'Almarai', sans-serif !important;
    }

    /* 2. إجبار الخط على كل النصوص الحقيقية */
    h1, h2, h3, h4, h5, h6, p, label, button, input, textarea, span {
        font-family: 'Almarai', sans-serif !important;
    }

    /* 3. 🔥 الحل النهائي للمستطيلات البيضاء 🔥 */
    /* استهداف حقول النص والإدخال */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        background-color: #0f172a !important; /* خلفية داكنة جداً */
        color: #ffffff !important;           /* نص أبيض */
        border: 1px solid #334155 !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 4. إخفاء أيقونة السهم وأي نص مرافق (arrow_right) */
    [data-testid="stExpanderToggleIcon"], .streamlit-expanderHeader svg {
        display: none !important;
        visibility: hidden !important;
    }

    /* 5. تنسيق البطاقات */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        display: block !important;
        border: none !important;
    }
    .streamlit-expanderHeader p {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        text-align: right !important;
        direction: rtl !important;
        color: white !important;
        margin: 0 !important;
    }

    /* 6. إعدادات اللابتوب */
    @media (min-width: 1000px) {
        .block-container { max-width: 85% !important; }
        h1 { font-size: 3.5rem !important; }
        p, label, input, .stButton button { font-size: 1.2rem !important; }
        .streamlit-expanderHeader p { font-size: 1.4rem !important; }
        .center-logo { width: 150px !important; }
    }

    /* أزرار التحميل */
    .dl-link {
        display: block; width: 100%; padding: 12px; margin: 8px 0;
        text-align: center; border-radius: 8px; text-decoration: none !important;
        font-weight: 700; color: white !important; border: 1px solid rgba(255,255,255,0.2);
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }

    .center-logo { display: block; margin: 0 auto 15px auto; width: 120px; height: auto; }
    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. الدوال ---
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
        vid_id = u.split("shorts/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={vid_id}"
    elif "youtu.be/" in u:
        vid_id = u.split("youtu.be/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={vid_id}"
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

# --- 5. الهيدر ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return None

logo_file = None
if os.path.exists("zain_logo_new.png"): logo_file = "zain_logo_new.png"
elif os.path.exists("zain_logo.png"): logo_file = "zain_logo.png"

if logo_file:
    img_b64 = get_img_as_base64(logo_file)
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="data:image/png;base64,{img_b64}" class="center-logo">
            <h1 style="margin: 0; color: white; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">مكتبة زين</h1>
            <p style="opacity: 0.9; color: #e2e8f0; margin-bottom: 20px;">مساحتك الخاصة للإبداع</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو")
    if st.button("🔍 جلب العنوان"):
        if url_in:
            t = get_youtube_title(url_in)
            if t:
                st.session_state.temp_title = t
                st.success("تم!")
    
    dt = st.session_state.get('temp_title', '')
    title_in = st.text_input("العنوان", value=dt)
    cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ ✅"):
        if title_in and url_in:
            st.session_state.videos.append({"title": title_in, "path": fix_youtube_url(url_in), "category": cat_in, "date": time.strftime("%Y-%m-%d")})
            save_to_disk()
            if 'temp_title' in st.session_state: del st.session_state.temp_title
            st.rerun()

tabs = st.tabs(["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
for i, cat in enumerate(["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]):
    with tabs[i]:
        vids = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        for idx, vid in enumerate(vids):
            with st.expander(f"🎥 {vid['title']}"):
                st.video(vid['path'])
                st_copy_to_clipboard(vid['path'], "📋 نسخ الرابط", key=f"cp_{cat}_{idx}")
                c1, c2 = st.columns(2)
                c1.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
                c2.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt</a>', unsafe_allow_html=True)
                if st.button("حذف 🗑️", key=f"del_{cat}_{idx}"):
                    st.session_state.videos.remove(vid)
                    save_to_disk()
                    st.rerun()
