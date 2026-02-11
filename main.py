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

# --- 3. إدارة الوضع (ليلي/نهاري) ---
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = 'dark'

# زر التبديل العلوي
col_mode, col_empty = st.columns([0.1, 0.9])
with col_mode:
    if st.button("🌓"):
        st.session_state.theme_mode = 'light' if st.session_state.theme_mode == 'dark' else 'dark'
        st.rerun()

# إعدادات الألوان واللوغو (دعم WebP كخيار أول)
if st.session_state.theme_mode == 'dark':
    bg_color, text_color = "#0f172a", "#ffffff"
    gradient = "radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%)"
    input_bg, header_bg = "rgba(255, 255, 255, 0.05)", "rgba(30, 41, 59, 0.7)"
    # ترتيب البحث عن لوغو الوضع الليلي
    possible_logos = ["zain_logo.webp", "zain_logo_new.png", "zain_logo.jpg", "zain_logo.png"]
else:
    bg_color, text_color = "#f8fafc", "#1e293b"
    gradient = "radial-gradient(circle at 50% 0%, #e2e8f0 0%, #f8fafc 70%)"
    input_bg, header_bg = "rgba(0, 0, 0, 0.05)", "rgba(226, 232, 240, 0.8)"
    # ترتيب البحث عن لوغو الوضع النهاري
    possible_logos = ["zain_logo_dark.webp", "zain_logo_dark.jpg", "zain_logo_dark.png"]

# --- 4. التصميم (CSS) المحسن للسرعة ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    html, body, .stApp {{
        background-color: {bg_color} !important;
        background-image: {gradient};
        background-attachment: fixed;
        color: {text_color} !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label, button, .stMarkdown p, .stButton button, .stTextInput input {{
        font-family: 'Almarai', sans-serif !important;
        color: {text_color} !important;
    }}
    
    [data-testid="stExpanderToggleIcon"], svg {{ display: none !important; visibility: hidden !important; }}

    .streamlit-expanderHeader {{
        background-color: {header_bg} !important;
        border-radius: 15px !important; padding: 15px 20px !important;
        margin-bottom: 12px; display: block !important; border: none !important;
    }}

    .stTextInput input, div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        direction: rtl !important; text-align: right !important;
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
    
    /* أزرار التحميل */
    .dl-link {{
        display: block; width: 100%; padding: 15px; margin: 10px 0;
        text-align: center; border-radius: 10px; text-decoration: none !important;
        font-weight: 700; color: white !important; border: 1px solid rgba(255,255,255,0.2);
    }}
    .savefrom-btn {{ background: linear-gradient(135deg, #10b981, #059669); }}
    .cobalt-btn {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
    </style>
""", unsafe_allow_html=True)

# --- 5. منطق الصور (WebP Support) ---
@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: data = f.read()
        return base64.b64encode(data).decode()
    except: return None

logo_to_show = None
for l_path in possible_logos:
    if os.path.exists(l_path):
        logo_to_show = l_path
        break

if logo_to_show:
    img_b64 = get_img_as_base64(logo_to_show)
    # تحديد نوع الصورة للمتصفح
    ext = logo_to_show.split('.')[-1]
    mime_type = "image/webp" if ext == "webp" else f"image/{ext.replace('jpg', 'jpeg')}"
    
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="data:{mime_type};base64,{img_b64}" class="center-logo">
            <h1 style="margin-top: 10px; font-size: 3rem; color: {text_color};">مكتبة زين</h1>
            <p style="opacity: 0.8; font-size: 1.1rem; margin-bottom: 20px;">مساحتك الخاصة للإبداع</p>
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
        v_id = u.split("shorts/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={v_id}"
    return u

# --- 7. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو")
    c1, c2 = st.columns(2)
    with c2: title_in = st.text_input("العنوان")
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ ✅"):
        if title_in and url_in:
            st.session_state.videos.append({
                "title": title_in, "path": fix_youtube_url(url_in), 
                "category": cat_in, "date": time.strftime("%Y-%m-%d")
            })
            save_to_disk()
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

for i, cat in enumerate(categories):
    with tabs[i]:
        items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        if not items: st.info("لا يوجد محتوى")
        for idx, vid in enumerate(items):
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
