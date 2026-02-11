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

# --- 2. دوال مساعدة وسريعة (Cached) ---
def toggle_theme():
    """دالة التبديل السريع"""
    st.session_state.theme_mode = 'light' if st.session_state.theme_mode == 'dark' else 'dark'

@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return None

@st.cache_data
def get_active_logo(mode):
    """تحديد اللوغو المناسب مرة واحدة فقط لتسريع التحميل"""
    if mode == 'dark':
        candidates = ["zain_logo.webp", "zain_logo_new.png", "zain_logo.png", "zain_logo.jpg"]
    else:
        candidates = ["zain_logo_dark.webp", "zain_logo_dark.jpg", "zain_logo_dark.png"]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

# --- 3. إدارة الوضع ---
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'dark'

# زر التبديل (مع Callback للسرعة)
col_mode, _ = st.columns([0.1, 0.9])
with col_mode:
    st.button("🌓", on_click=toggle_theme, help="تبديل الوضع")

# إعداد المتغيرات حسب الوضع
if st.session_state.theme_mode == 'dark':
    vars = {
        "bg": "#0f172a", "text": "#ffffff",
        "grad": "radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%)",
        "inp": "rgba(255, 255, 255, 0.05)", "head": "rgba(30, 41, 59, 0.7)"
    }
else:
    vars = {
        "bg": "#f8fafc", "text": "#1e293b",
        "grad": "radial-gradient(circle at 50% 0%, #e2e8f0 0%, #f8fafc 70%)",
        "inp": "rgba(0, 0, 0, 0.05)", "head": "rgba(226, 232, 240, 0.8)"
    }

# --- 4. CSS المحسن ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    html, body, .stApp {{
        background-color: {vars['bg']} !important;
        background-image: {vars['grad']};
        background-attachment: fixed;
        color: {vars['text']} !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label, button, .stMarkdown p, .stButton button, .stTextInput input {{
        font-family: 'Almarai', sans-serif !important;
        color: {vars['text']} !important;
    }}
    
    [data-testid="stExpanderToggleIcon"], svg {{ display: none !important; visibility: hidden !important; }}

    .streamlit-expanderHeader {{
        background-color: {vars['head']} !important;
        border-radius: 15px !important; padding: 15px 20px !important;
        margin-bottom: 12px; display: block !important; border: none !important;
    }}

    .stTextInput input, div[data-baseweb="select"] > div {{
        background-color: {vars['inp']} !important;
        color: {vars['text']} !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        direction: rtl !important; text-align: right !important;
        -webkit-text-fill-color: {vars['text']} !important;
    }}

    @media (min-width: 1000px) {{
        .block-container {{ max-width: 90% !important; padding-top: 1rem !important; }}
        h1 {{ font-size: 4rem !important; }}
        p, label, .stButton button {{ font-size: 1.25rem !important; }}
        .streamlit-expanderHeader p {{ font-size: 1.5rem !important; }}
        .center-logo {{ width: 160px !important; }}
    }}

    .center-logo {{ display: block; margin-left: auto; margin-right: auto; width: 130px; height: auto; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .stTabs [data-baseweb="tab-list"] {{ justify-content: center; flex-direction: row-reverse; gap: 15px; }}
    
    .dl-link {{
        display: block; width: 100%; padding: 15px; margin: 10px 0;
        text-align: center; border-radius: 10px; text-decoration: none !important;
        font-weight: 700; color: white !important; border: 1px solid rgba(255,255,255,0.2);
    }}
    .savefrom-btn {{ background: linear-gradient(135deg, #10b981, #059669); }}
    .cobalt-btn {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
    </style>
""", unsafe_allow_html=True)

# --- 5. عرض اللوغو ---
logo_path = get_active_logo(st.session_state.theme_mode)
if logo_path:
    img_b64 = get_img_as_base64(logo_path)
    ext = logo_path.split('.')[-1]
    mime = "image/webp" if ext == "webp" else f"image/{ext.replace('jpg', 'jpeg')}"
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="data:{mime};base64,{img_b64}" class="center-logo">
            <h1 style="margin-top: 10px; font-size: 3rem; color: {vars['text']}; text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);">مكتبة زين</h1>
            <p style="opacity: 0.9; font-size: 1.2rem; margin: 5px 0 20px 0; font-weight: 300;">مساحتك الخاصة للإبداع</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)

# --- 6. إدارة البيانات ---
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
    u = url.strip()
    if "shorts/" in u:
        return f"https://www.youtube.com/watch?v={u.split('shorts/')[-1].split('?')[0]}"
    elif "youtu.be/" in u:
        return f"https://www.youtube.com/watch?v={u.split('youtu.be/')[-1].split('?')[0]}"
    return u

def get_youtube_title(url):
    try:
        clean = fix_youtube_url(url)
        res = requests.get(f"https://www.youtube.com/oembed?url={clean}&format=json", timeout=3)
        if res.status_code == 200: return res.json().get('title')
    except: pass
    return None

# --- 7. الإدخال ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو")
    if st.button("🔍 جلب العنوان"):
        if url_in:
            t = get_youtube_title(url_in)
            if t:
                st.session_state.temp_title = t
                st.success("تم!")
            else: st.warning("يدوياً")
    
    dt = st.session_state.get('temp_title', '')
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان", value=dt)
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ ✅"):
        if title_in and url_in:
            st.session_state.videos.append({
                "title": title_in, "path": fix_youtube_url(url_in), 
                "category": cat_in, "date": time.strftime("%Y-%m-%d")
            })
            save_to_disk()
            if 'temp_title' in st.session_state: del st.session_state.temp_title
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

# --- 8. الصفحات (Optimized: 5 Videos) ---
VIDEOS_PER_PAGE = 5 # تقليل العدد لزيادة سرعة التبديل

if 'page_num' not in st.session_state:
    st.session_state.page_num = 0

for i, cat in enumerate(categories):
    with tabs[i]:
        all_items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        
        if not all_items:
            st.info("لا يوجد محتوى")
        else:
            total_pages = max(1, (len(all_items) + VIDEOS_PER_PAGE - 1) // VIDEOS_PER_PAGE)
            current_page = min(max(0, st.session_state.page_num), total_pages - 1)
            
            start = current_page * VIDEOS_PER_PAGE
            end = start + VIDEOS_PER_PAGE
            page_items = all_items[start:end]
            
            for idx, vid in enumerate(page_items):
                unique_key = f"{cat}_{start + idx}"
                with st.expander(f"🎥 {vid['title']}"):
                    st.video(vid['path'])
                    st_copy_to_clipboard(vid['path'], "📋 نسخ", key=f"cp_{unique_key}")
                    c1, c2 = st.columns(2)
                    c1.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom</a>', unsafe_allow_html=True)
                    c2.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt</a>', unsafe_allow_html=True)
                    if st.button("حذف 🗑️", key=f"del_{unique_key}"):
                        st.session_state.videos.remove(vid)
                        save_to_disk()
                        st.rerun()
            
            st.markdown("---")
            c_prev, c_info, c_next = st.columns([1, 2, 1])
            with c_prev:
                if current_page > 0:
                    if st.button("السابق ⬅️", key=f"prev_{cat}"):
                        st.session_state.page_num -= 1
                        st.rerun()
            with c_info:
                st.markdown(f"<div style='text-align: center; direction: rtl;'>صفحة {current_page + 1} من {total_pages}</div>", unsafe_allow_html=True)
            with c_next:
                if current_page < total_pages - 1:
                    if st.button("التالي ➡️", key=f"next_{cat}"):
                        st.session_state.page_num += 1
                        st.rerun()
