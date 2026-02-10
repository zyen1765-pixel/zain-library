import streamlit as st
import json
import os
import time
import base64
import requests
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة والأيقونة الجديدة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="📚", # تم التغيير إلى كتب
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. نظام الحماية (كلمة السر) ---
# قم بتغيير "12345" إلى كلمة السر التي تريدها
PASSWORD = "9988"

def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # واجهة تسجيل الدخول
    st.markdown("""
        <style>
        .stTextInput input { text-align: center; direction: ltr; }
        h1 {text-align: center; color: white;}
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🔒 المكتبة محمية")
    pwd_input = st.text_input("أدخل كلمة المرور للدخول:", type="password")
    
    if st.button("دخول 🔓"):
        if pwd_input == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور خاطئة")
    return False

if not check_password():
    st.stop() # يوقف التطبيق هنا إذا لم تكن كلمة السر صحيحة

# --- 3. التصميم (CSS) ---
st.markdown("""
    <style>
    /* استيراد خط المراعي */
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

    html, body, .stApp {
        font-family: 'Almarai', sans-serif;
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, button, input, textarea {
        font-family: 'Almarai', sans-serif !important;
        text-align: right;
    }

    /* إخفاء أيقونة السهم */
    .streamlit-expanderHeader svg, 
    .streamlit-expanderHeader [data-testid="stExpanderToggleIcon"] {
        display: none !important;
    }

    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px;
        color: white !important;
        padding: 15px !important;
        display: block !important; 
    }

    .streamlit-expanderHeader p {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-align: right !important;
        width: 100% !important;
        display: block !important;
    }

    .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.3) !important;
        border-radius: 0 0 12px 12px;
        border-top: none;
        text-align: right !important;
    }

    .stTextInput input {
        color: white !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        direction: rtl !important;
        text-align: right !important;
    }

    .app-icon {
        width: 100px; height: 100px; 
        object-fit: contain; 
        background-color: white;
        border-radius: 20px; 
        border: 4px solid #ffffff; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        display: block; 
    }

    /* أزرار التحميل */
    .dl-link {
        display: block;
        width: 100%;
        padding: 12px;
        margin: 8px 0;
        text-align: center;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: 700;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .savefrom-btn { background: linear-gradient(135deg, #10b981, #059669); }
    .cobalt-btn { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    
    .dl-link:hover { opacity: 0.9; transform: translateY(-2px); }

    #MainMenu, footer, header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        flex-direction: row-reverse; 
        gap: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. إدارة الملفات والدوال المساعدة ---
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
    if "youtu.be/" in u:
        vid_id = u.split("youtu.be/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={vid_id}"
    if "instagram.com" in u: u = u.split("?")[0]
    return u

# دالة جلب عنوان الفيديو (جديد)
def get_youtube_title(url):
    try:
        clean_url = fix_youtube_url(url)
        # نستخدم خدمة oEmbed الرسمية من يوتيوب (لا تحتاج مفتاح سري)
        oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
        response = requests.get(oembed_url, timeout=5)
        if response.status_code == 200:
            return response.json().get('title')
    except:
        pass
    return None

# --- 5. الهيدر واللوغو ---
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
            <div style="text-align: right; padding-top: 15px;">
                <h1 style="margin: 0; font-size: 3.5rem; color: white; text-shadow: 0 0 20px rgba(56, 189, 248, 0.5);">مكتبة زين</h1>
                <p style="opacity: 0.9; font-size: 1.2rem; color: #e2e8f0; margin: 0; font-weight: 300;">مساحتك الخاصة للإبداع</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align:center;'>مكتبة زين</h1>", unsafe_allow_html=True)

# --- 6. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    # ترتيب العناصر: الرابط أولاً لكي نجلب العنوان منه
    url_in = st.text_input("رابط الفيديو")
    
    # زر لجلب العنوان تلقائياً
    if st.button("🔍 جلب العنوان تلقائياً"):
        if url_in:
            fetched_title = get_youtube_title(url_in)
            if fetched_title:
                st.session_state.temp_title = fetched_title
                st.success("تم جلب العنوان بنجاح!")
            else:
                st.warning("لم نتمكن من جلب العنوان، يرجى كتابته يدوياً.")
    
    # استخدام العنوان المجلوب إذا وجد
    default_title = st.session_state.get('temp_title', '')
    
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان", value=default_title)
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ الفيديو ✅"):
        if title_in and url_in:
            final_url = fix_youtube_url(url_in)
            st.session_state.videos.append({"title": title_in, "path": final_url, "category": cat_in, "type": "url", "date": time.strftime("%Y-%m-%d")})
            save_to_disk()
            # مسح العنوان المؤقت
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
        
        # 1. نسخ الرابط
        st.write("##### 1️⃣ انسخ الرابط:")
        st_copy_to_clipboard(item['path'], "📋 اضغط للنسخ", key=f"copy_{unique_key}")
        
        # 2. أزرار التحميل
        st.write("##### 2️⃣ اختر التحميل المناسب:")
        
        c1, c2 = st.columns(2)
        with c1:
            # SaveFrom (للفيديوهات الطويلة)
            st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom (فيديوهات)</a>', unsafe_allow_html=True)
        with c2:
            # Cobalt (للشورتس - أفضل حل حالياً)
            st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">🔵 Cobalt (شورتس)</a>', unsafe_allow_html=True)
        
        st.caption("💡 نصيحة: إذا كان الفيديو **Shorts** استخدم الزر الأزرق (Cobalt).")

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
