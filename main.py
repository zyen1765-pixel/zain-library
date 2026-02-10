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

# --- 3. التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    :root {
        --primary-color: #38bdf8;
        --background-color: #0f172a;
        --secondary-background-color: #1e293b;
        --text-color: #ffffff;
    }

    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, button, input, textarea, [data-testid="stMarkdownContainer"] p {
        font-family: 'Almarai', sans-serif !important;
    }

    /* تحسين شكل الـ Expander وإخفاء الأيقونة بشكل صحيح */
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }
    
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border-radius: 15px !important;
        direction: rtl !important;
    }

    .streamlit-expanderHeader p {
        text-align: right !important;
        font-weight: bold !important;
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        text-align: right !important;
    }

    .dl-link {
        display: block; width: 100%; padding: 15px; margin: 10px 0;
        text-align: center; border-radius: 10px; text-decoration: none !important;
        font-weight: 700; color: white !important;
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    
    .center-logo {
        display: block; margin: 0 auto;
        width: 150px; height: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. إدارة الملفات ---
DB_FILE = "zain_library.json"

if 'videos' not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                st.session_state.videos = json.load(f)
        except:
            st.session_state.videos = []
    else:
        st.session_state.videos = []

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
    return u

def get_youtube_title(url):
    try:
        clean_url = fix_youtube_url(url)
        oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
        # إضافة Header لضمان الموافقة على الطلب
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(oembed_url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json().get('title')
    except:
        pass
    return None

# --- 5. الهيدر ---
logo_file = "zain_logo.png" # تأكد من وجود الملف أو غير الاسم
if os.path.exists(logo_file):
    with open(logo_file, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/png;base64,{img_b64}" class="center-logo">', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>مكتبة زين</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.8;'>مساحتك الخاصة للإبداع</p>", unsafe_allow_html=True)

# --- 6. إضافة فيديو جديد ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو (يوتيوب أو شورتس)")
    
    if st.button("🔍 جلب العنوان"):
        if url_in:
            fetched_title = get_youtube_title(url_in)
            if fetched_title:
                st.session_state.temp_title = fetched_title
                st.success(f"تم العثور على: {fetched_title}")
            else:
                st.error("تعذر جلب العنوان، اكتبه يدوياً")

    title_in = st.text_input("العنوان", value=st.session_state.get('temp_title', ''))
    cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ ✅"):
        if title_in and url_in:
            new_video = {
                "id": str(time.time()), # معرف فريد للحذف الآمن
                "title": title_in,
                "path": fix_youtube_url(url_in),
                "category": cat_in,
                "date": time.strftime("%Y-%m-%d")
            }
            st.session_state.videos.append(new_video)
            save_to_disk()
            if 'temp_title' in st.session_state:
                del st.session_state.temp_title
            st.rerun()

st.markdown("---")

# --- 7. عرض المحتوى ---
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

for i, cat in enumerate(categories):
    with tabs[i]:
        # تصفية الفيديوهات حسب القسم
        filtered_items = [v for v in st.session_state.videos if cat == "الكل" or v['category'] == cat]
        
        if not filtered_items:
            st.info("لا يوجد فيديوهات في هذا القسم حالياً")
        
        for vid in reversed(filtered_items):
            with st.expander(f"🎥 {vid['title']}"):
                # عرض الفيديو
                st.video(vid['path'])
                
                # أدوات
                st.write("---")
                st.write("##### 📋 نسخ الرابط")
                st_copy_to_clipboard(vid['path'], "اضغط للنسخ", key=f"copy_{vid['id']}")
                
                st.write("##### 📥 روابط التحميل الخارجي")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt</a>', unsafe_allow_html=True)
                
                st.caption(f"📅 أضيف في: {vid['date']}")
                
                # زر الحذف باستخدام المعرف الفريد
                if st.button("🗑️ حذف الفيديو", key=f"del_{vid['id']}"):
                    st.session_state.videos = [v for v in st.session_state.videos if v['id'] != vid['id']]
                    save_to_disk()
                    st.rerun()
