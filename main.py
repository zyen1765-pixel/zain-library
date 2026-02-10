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

# --- 2. التصميم (CSS) - النسخة المحسنة للألوان ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    
    /* 1. إجبار الخط الأبيض والخلفية الغامقة على جميع الأجهزة */
    html, body, [class*="css"], .stApp { 
        font-family: 'Cairo', sans-serif !important; 
        color: #ffffff !important; 
    }
    
    :root { 
        --bg-dark: #0f172a; 
        --primary: #38bdf8; 
    }
    
    .stApp { 
        background-color: var(--bg-dark) !important; 
        background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%); 
        background-attachment: fixed; 
    }
    
    /* إصلاح لون النصوص داخل العناوين والفقرات */
    h1, h2, h3, h4, h5, h6, p, label, div, span { 
        color: white !important; 
        text-align: right; 
    }
    
    /* إصلاح لون الكتابة داخل مربعات الإدخال */
    .stTextInput input, .stSelectbox div {
        color: white !important;
    }

    /* 2. تنسيق اللوغو */
    .app-icon {
        width: 100px; height: 100px; object-fit: contain; background-color: white;
        border-radius: 20px; border: 3px solid #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        display: block; 
    }
    
    /* 3. تنسيق البطاقات */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.7); 
        border: 1px solid rgba(255,255,255,0.1); 
        border-radius: 10px;
        color: white !important; 
        direction: rtl;
    }
    .streamlit-expanderContent { 
        background-color: rgba(0,0,0,0.2); 
        border-radius: 0 0 10px 10px; 
        border-top: none; 
    }
    
    /* 4. تنسيق أزرار التحميل */
    .dl-link {
        display: block;
        width: 100%;
        padding: 12px;
        margin: 5px 0;
        text-align: center;
        border-radius: 8px;
        text-decoration: none !important;
        font-weight: bold;
        color: white !important;
        transition: 0.3s;
        border: 1px solid rgba(255,255,255,0.1);
        font-size: 0.9rem;
    }
    .savefrom-btn { background: linear-gradient(45deg, #10b981, #059669); } 
    .snapsave-btn { background: linear-gradient(45deg, #0ea5e9, #0284c7); } 
    .y2mate-btn { background: linear-gradient(45deg, #ef4444, #b91c1c); } 
    
    .dl-link:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }

    #MainMenu, footer, header {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] { justify-content: center; flex-direction: row-reverse; }
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
            <div style="text-align: right; padding-top: 10px;">
                <h1 style="margin: 0; font-size: 3rem; color: white;">مكتبة زين</h1>
                <p style="opacity: 0.8; font-size: 1.1rem; color: #ccc; margin: 0;">مساحتك الخاصة للإبداع</p>
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
    
    with st.expander(f"{icon} {item['title']}  |  📅 {item['date']}"):
        if "youtube.com" in item['path'] or "youtu.be" in item['path']:
            st.video(item['path'])
        else: st.info(f"رابط خارجي: {item['path']}")

        st.markdown("---")
        
        # 1. نسخ الرابط
        st.write("##### 1️⃣ انسخ الرابط:")
        st_copy_to_clipboard(item['path'], "📋 اضغط هنا للنسخ", key=f"copy_{unique_key}")
        
        # 2. أزرار المواقع
        st.write("##### 2️⃣ اختر موقع التحميل:")
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f'<a href="https://en.savefrom.net/" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom (فيديوهات)</a>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<a href="https://snapsave.io/en" target="_blank" class="dl-link snapsave-btn">🔵 SnapSave (للشورتس)</a>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<a href="https://www.y2mate.com/en/youtube-shorts-downloader" target="_blank" class="dl-link y2mate-btn">🔴 Y2Mate (احتياطي)</a>', unsafe_allow_html=True)

        st.caption("💡 نصيحة: للشورتس استخدم الزر الأزرق (SnapSave).")

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
