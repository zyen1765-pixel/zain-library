import streamlit as st
import json
import os
import time
import base64

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    :root { --bg-dark: #0f172a; --primary: #38bdf8; --glass: rgba(30, 41, 59, 0.7); }
    .stApp { background-color: var(--bg-dark) !important; background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%); background-attachment: fixed; }
    
    h1 { font-weight: 900 !important; color: white !important; }
    h3, p, label, div, span { text-align: right; }
    
    .app-icon {
        width: 100px; height: 100px; object-fit: contain; background-color: white;
        border-radius: 20px; border: 3px solid #ffffff; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        display: block; 
    }
    
    .streamlit-expanderHeader {
        background-color: var(--glass); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
        color: white !important; direction: rtl;
    }
    .streamlit-expanderContent { background-color: rgba(0,0,0,0.2); border-radius: 0 0 10px 10px; border-top: none; }
    
    /* تنسيق الأزرار */
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
    .savefrom-btn { background: linear-gradient(45deg, #10b981, #059669); } /* الأخضر الأساسي */
    .publer-btn { background: linear-gradient(45deg, #16a34a, #15803d); } /* أخضر غامق */
    .cobalt-btn { background: linear-gradient(45deg, #3b82f6, #2563eb); } /* أزرق */
    
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
    if "youtube.com/shorts/" in u: u = u.replace("shorts/", "watch?v=")
    elif "youtu.be/" in u:
        vid_id = u.split("youtu.be/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={vid_id}"
    if "instagram.com" in u: u = u.split("?")[0]
    return u

# --- 4. الهيدر واللوغو ---
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
        
        # 1. قسم النسخ
        st.write("##### 1️⃣ انسخ الرابط:")
        st.code(item['path'], language="text")
        
        # 2. قسم التحميل
        st.write("##### 2️⃣ اختر موقع التحميل:")
        
        # تحضير رابط SaveFrom (SSYoutube)
        # نقوم باستبدال الدومين ليفتح الموقع مباشرة
        ss_link = item['path'].replace("www.youtube.com", "ssyoutube.com").replace("youtube.com", "ssyoutube.com")

        c1, c2, c3 = st.columns(3)
        
        with c1:
            # الخيار الأول: SaveFrom
            st.markdown(f'<a href="{ss_link}" target="_blank" class="dl-link savefrom-btn">🟢 SaveFrom (صوت/فيديو)</a>', unsafe_allow_html=True)
        with c2:
            # الخيار الثاني: Publer (للشورتس)
            st.markdown(f'<a href="https://publer.io/tools/media-downloader" target="_blank" class="dl-link publer-btn">🔥 Publer (للشورتس)</a>', unsafe_allow_html=True)
        with c3:
            # الخيار الثالث: Cobalt (الأنظف)
            st.markdown(f'<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">💎 Cobalt (بدون إعلانات)</a>', unsafe_allow_html=True)

        st.caption("💡 ملاحظة: استخدم **SaveFrom** للفيديوهات العادية، واستخدم **Publer** إذا كان الفيديو **Shorts**.")

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
