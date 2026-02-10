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
        h1 {text-align: center; color: white !important; font-family: sans-serif;}
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

# --- 3. التصميم (CSS) - النسخة المضادة للألوان البيضاء ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    /* 1. إجبار الوضع الداكن الكلي */
    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
        font-family: 'Almarai', sans-serif !important;
    }

    /* 2. حذف السهم وأي نصوص برمجية مرافقة له نهائياً */
    [data-testid="stExpanderToggleIcon"], svg, .streamlit-expanderHeader::after {
        display: none !important;
        visibility: hidden !important;
    }

    /* 3. 🔥 الحل النهائي للمستطيلات البيضاء (Laptop Fix) 🔥 */
    /* استهداف حقول الإدخال ومنع المتصفح من تغيير ألوانها */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #1e293b !important; /* لون كحلي غامق صلب */
        color: #ffffff !important; /* نص أبيض صلب */
        border: 1px solid #334155 !important;
        -webkit-text-fill-color: #ffffff !important; /* إجبار المتصفح على تلوين النص */
    }

    /* إصلاح لون النص عند الكتابة */
    .stTextInput input, .stTextArea textarea {
        color: white !important;
        background-color: #1e293b !important;
    }

    /* إصلاح القوائم المنسدلة على اللابتوب */
    div[data-baseweb="select"] {
        background-color: #1e293b !important;
        color: white !important;
    }

    /* 4. تنسيق البطاقات (Expander) */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        margin-bottom: 12px;
        display: block !important;
    }
    .streamlit-expanderHeader p {
        font-weight: 700 !important;
        margin: 0 !important;
        text-align: right !important;
        width: 100% !important;
        direction: rtl !important;
        color: white !important;
    }

    /* 5. 💻 تكبير الخط للابتوب 💻 */
    @media (min-width: 1000px) {
        .block-container { max-width: 85% !important; padding-top: 1rem !important; }
        h1 { font-size: 4rem !important; }
        p, label, button, input { font-size: 1.3rem !important; }
        .streamlit-expanderHeader p { font-size: 1.6rem !important; }
        .center-logo { width: 170px !important; }
    }

    /* أزرار التحميل */
    .dl-link {
        display: block; width: 100%; padding: 15px; margin: 10px 0;
        text-align: center; border-radius: 10px; text-decoration: none !important;
        font-weight: 700; color: white !important; border: 1px solid rgba(255,255,255,0.2);
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }

    .center-logo { display: block; margin: 0 auto 15px auto; width: 130px; height: auto; }
    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; gap: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. الدوال وإدارة الملفات ---
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

# --- 5. الهيدر وتوسيط اللوغو ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return None

logo_file = None
if os.path.exists("zain_logo_new.png"): logo_file = "zain_logo_new.png"
elif os.path.exists("zain_logo.png"): logo_file = "zain_logo.png"
elif os.path.exists("zain_logo.jpg"): logo_file = "zain_logo.jpg"

if logo_file:
    img_b64 = get_img_as_base64(logo_file)
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="data:image/png;base64,{img_b64}" class="center-logo">
            <h1 style="margin-top: 10px; font-size: 3rem; color: white; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">مكتبة زين</h1>
            <p style="opacity: 0.9; font-size: 1.2rem; color: #e2e8f0; margin: 5px 0 20px 0; font-weight: 300;">مساحتك الخاصة للإبداع</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)

# --- 6. الواجهة الرئيسية ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو", key="url_input")
    if st.button("🔍 جلب العنوان"):
        if url_in:
            fetched_title = get_youtube_title(url_in)
            if fetched_title:
                st.session_state.temp_title = fetched_title
                st.success("تم جلب العنوان!")
            else: st.warning("اكتب العنوان يدوياً")
    
    default_title = st.session_state.get('temp_title', '')
    title_in = st.text_input("العنوان", value=default_title, key="title_input")
    cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"], key="cat_input")
    
    if st.button("حفظ الفيديو ✅"):
        if title_in and url_in:
            final_url = fix_youtube_url(url_in)
            st.session_state.videos.append({"title": title_in, "path": final_url, "category": cat_in, "date": time.strftime("%Y-%m-%d")})
            save_to_disk()
            if 'temp_title' in st.session_state: del st.session_state.temp_title
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

def show_card(item, idx, cat_name):
    unique_key = f"{cat_name}_{idx}"
    label = f"🎥 {item['title']}"
    
    with st.expander(label):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"الرابط: {item['path']}")

        st.markdown("---")
        st.write("##### 1️⃣ نسخ الرابط:")
        st_copy_to_clipboard(item['path'], "📋 نسخ الرابط", key=f"copy_{unique_key}")
        
        st.write("##### 2️⃣ التحميل:")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
        with c2: st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt (Shorts)</a>', unsafe_allow_html=True)
        
        st.caption(f"📅 تاريخ الإضافة: {item['date']}")
        if st.button("حذف 🗑️", key=f"del_{unique_key}"):
            st.session_state.videos.remove(item)
            save_to_disk()
            st.rerun()

for i, cat in enumerate(categories):
    with tabs[i]:
        items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        if not items: st.info("لا يوجد محتوى حالياً")
        for idx, vid in enumerate(items):
            show_card(vid, idx, cat)
