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
        h1 {text-align: center; color: white !important; font-family: 'Almarai', sans-serif;}
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
        --text-color: #ffffff;
    }

    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, button, input, textarea, .stMarkdown, div, span {
        font-family: 'Almarai', sans-serif !important;
    }

    /* تحسين إخفاء الأيقونة وجعل النص في المنتصف/اليمين */
    [data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    h2, h3, h4, h5, h6, p, label {
        text-align: right !important;
        direction: rtl !important;
    }

    /* تنسيق البطاقات */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border-radius: 15px !important;
        padding: 15px 20px !important;
        direction: rtl !important;
    }

    .streamlit-expanderHeader p {
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }

    /* أزرار التحميل */
    .dl-link {
        display: block; width: 100%; padding: 12px; margin: 8px 0;
        text-align: center; border-radius: 10px; text-decoration: none !important;
        font-weight: 700; color: white !important;
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    
    .center-logo {
        display: block; margin-left: auto; margin-right: auto;
        width: 130px; height: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. إدارة البيانات ---
DB_FILE = "zain_library.json"

if 'videos' not in st.session_state:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            st.session_state.videos = json.load(f)
    else:
        st.session_state.videos = []

def save_to_disk():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.videos, f, ensure_ascii=False, indent=4)

def fix_youtube_url(url):
    u = url.strip()
    if "shorts/" in u:
        video_id = u.split("shorts/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    return u.split("?")[0] if "instagram.com" in u else u

def get_youtube_title(url):
    try:
        clean_url = fix_youtube_url(url)
        response = requests.get(f"https://www.youtube.com/oembed?url={clean_url}&format=json", timeout=5)
        if response.status_code == 200:
            return response.json().get('title')
    except:
        return None
    return None

# --- 5. الهيدر ---
st.markdown("""
    <div style="text-align: center;">
        <h1 style="font-size: 3rem; color: white; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">مكتبة زين</h1>
        <p style="opacity: 0.8;">مساحتك الخاصة لتنظيم الفيديوهات والإبداع</p>
    </div>
""", unsafe_allow_html=True)

# --- 6. إضافة محتوى جديد ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_input = st.text_input("رابط الفيديو (YouTube, Shorts, etc.)", key="new_url")
    
    # تحسين جلب العنوان
    if st.button("🔍 جلب بيانات الفيديو"):
        if url_input:
            with st.spinner("جاري جلب العنوان..."):
                title = get_youtube_title(url_input)
                if title:
                    st.session_state.temp_title = title
                    st.success(f"تم العثور على: {title}")
                else:
                    st.error("تعذر جلب العنوان تلقائياً، يرجى إدخاله يدوياً")
        else:
            st.warning("يرجى وضع الرابط أولاً")

    current_title = st.text_input("عنوان الفيديو", value=st.session_state.get('temp_title', ''), key="title_field")
    category = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])

    if st.button("حفظ في المكتبة ✅"):
        if url_input and current_title:
            new_entry = {
                "title": current_title,
                "path": fix_youtube_url(url_input),
                "category": category,
                "date": time.strftime("%Y-%m-%d")
            }
            st.session_state.videos.append(new_entry)
            save_to_disk()
            st.session_state.temp_title = "" # تفريغ العنوان المؤقت
            st.success("تم الحفظ بنجاح!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("يرجى ملء الرابط والعنوان")

# --- 7. عرض المحتوى ---
st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

for i, cat in enumerate(categories):
    with tabs[i]:
        # فلترة الفيديوهات حسب القسم
        filtered_videos = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        
        if not filtered_videos:
            st.info("لا يوجد فيديوهات في هذا القسم حالياً.")
        
        for idx, vid in enumerate(filtered_videos):
            with st.expander(f"🎥 {vid['title']}"):
                # عرض الفيديو
                if "youtube.com" in vid['path'] or "youtu.be" in vid['path']:
                    st.video(vid['path'])
                else:
                    st.info(f"رابط: {vid['path']}")
                
                st.markdown("---")
                
                # أدوات التحكم
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📋 **نسخ الرابط:**")
                    st_copy_to_clipboard(vid['path'], "اضغط للنسخ", key=f"cp_{cat}_{idx}")
                
                with col2:
                    st.write("📥 **روابط التحميل:**")
                    st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt</a>', unsafe_allow_html=True)
                
                st.caption(f"📅 أضيف بتاريخ: {vid['date']}")
                
                if st.button("حذف الفيديو 🗑️", key=f"del_{cat}_{idx}"):
                    st.session_state.videos.remove(vid)
                    save_to_disk()
                    st.rerun()
