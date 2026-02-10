import streamlit as st
import json
import os
import time
import base64
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. التصميم (CSS) - النسخة المانعة للتداخل (Gap Method) ---
st.markdown("""
    <style>
    /* استيراد الخط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');

    /* تطبيق الخط العام على النصوص فقط */
    html, body, .stApp {
        background-color: #0f172a !important;
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    /* استهداف النصوص */
    h1, h2, h3, h4, h5, h6, p, div, span, label, button, input {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    /* استثناء الأيقونات للحفاظ عليها */
    svg, i { font-family: sans-serif !important; }

    /* محاذاة عامة لليمين */
    h1, h2, h3, h4, h5, h6, p, label {
        text-align: right !important;
    }

    /* --- إصلاح البطاقات (Expander) باستخدام الفراغ الإجباري --- */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px;
        color: white !important;
        
        /* الترتيب السحري لمنع التداخل */
        display: flex !important;
        flex-direction: row-reverse !important; /* النص يمين، السهم يسار */
        align-items: center !important;
        justify-content: space-between !important;
        gap: 20px !important; /* مسافة إجبارية مستحيل تجاوزها */
        padding: 15px !important;
    }

    /* تنسيق النص داخل العنوان */
    .streamlit-expanderHeader p {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        text-align: right !important;
        flex-grow: 1 !important; /* يأخذ كل المساحة المتاحة */
        width: 100% !important;
    }

    /* تنسيق أيقونة السهم */
    .streamlit-expanderHeader svg {
        min-width: 24px !important; /* حجز مكان ثابت للسهم */
        color: #38bdf8 !important;
    }

    /* المحتوى الداخلي */
    .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.3) !important;
        border-radius: 0 0 12px 12px;
        border-top: none;
        text-align: right !important;
    }

    /* تنسيق حقول الإدخال */
    .stTextInput input {
        color: white !important;
        text-align: right !important;
        direction: rtl !important;
    }

    /* تنسيق اللوغو */
    .app-icon {
        width: 110px; height: 110px; 
        object-fit: contain; 
        background-color: white;
        border-radius: 25px; 
        border: 4px solid #ffffff; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        display: block; 
    }

    /* زر التحميل */
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
        background: linear-gradient(135deg, #10b981, #059669);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .dl-link:hover { opacity: 0.9; transform: translateY(-2px); }

    #MainMenu, footer, header {visibility: hidden;}
    
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        flex-direction: row-reverse; 
        gap: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. إدارة الملفات ---
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

# --- 4. الهيدر ---
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

# --- 5. الواجهة ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان")
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    url_in = st.text_input("رابط الفيديو")
    if st.button("حفظ ✅"):
        if title_in and url_in:
            final_url = fix_youtube_url(url_in)
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
    
    # تحسين عرض العنوان والتاريخ
    label = f"{item['title']} | 📅 {item['date']}"
    
    with st.expander(label):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("---")
        
        # 1. نسخ الرابط
        st.write("##### 1️⃣ انسخ الرابط:")
        st_copy_to_clipboard(item['path'], "📋 اضغط للنسخ", key=f"copy_{unique_key}")
        
        # 2. زر التحميل
        st.write("##### 2️⃣ التحميل:")
        st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link">🚀 الذهاب لصفحة التحميل (SaveFrom)</a>', unsafe_allow_html=True)
        
        st.caption("💡 هذا الموقع هو الأفضل حالياً. انسخ الرابط وألصقه هناك.")

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
