import streamlit as st
import json
import os
import time
import base64
import requests
from st_copy_to_clipboard import st_copy_to_clipboard

# =========================================================
# 1) إعدادات الصفحة
# =========================================================
st.set_page_config(
    page_title="مكتبة زين",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2) نظام الحماية (محسّن)
# =========================================================
PASSWORD = st.secrets.get("APP_PASSWORD", "")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("""
        <style>
        .stApp { background-color: #0f172a !important; color: white !important; }
        .stTextInput input {
            text-align: center;
            color: white !important;
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
        }
        h1 { text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔒 المكتبة محمية")
    pwd = st.text_input("أدخل كلمة المرور", type="password")

    if st.button("دخول 🔓"):
        if pwd == PASSWORD:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة")

    return False

if not check_password():
    st.stop()

# =========================================================
# 3) CSS (كما هو مع تحسينات طفيفة)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');

html, body, .stApp {
    background-color: #0f172a !important;
    background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
    color: white !important;
}

* {
    font-family: 'Almarai', sans-serif !important;
    direction: rtl;
}

[data-testid="stExpanderToggleIcon"] {
    display: none !important;
}

.streamlit-expanderHeader {
    font-size: 0 !important;
    background-color: rgba(30, 41, 59, 0.7) !important;
    border-radius: 15px !important;
    padding: 15px 20px !important;
}

.streamlit-expanderHeader p {
    font-size: 1.2rem !important;
    font-weight: 700;
}

.dl-link {
    display: block;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    color: white !important;
    text-decoration: none !important;
}

.savefrom-btn {
    background: linear-gradient(135deg, #10b981, #059669);
}

.cobalt-btn {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}

#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 4) إدارة البيانات
# =========================================================
DB_FILE = "zain_library.json"

if "videos" not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                st.session_state.videos = json.load(f)
        except Exception:
            st.session_state.videos = []
    else:
        st.session_state.videos = []

def save_to_disk():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.videos, f, ensure_ascii=False, indent=4)

# =========================================================
# 5) أدوات يوتيوب
# =========================================================
def fix_youtube_url(url: str) -> str:
    if not url:
        return ""

    u = url.strip()

    if "m.youtube.com" in u:
        u = u.replace("m.youtube.com", "www.youtube.com")

    if "youtube.com/shorts/" in u:
        video_id = u.split("shorts/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={video_id}"

    elif "youtu.be/" in u:
        video_id = u.split("youtu.be/")[-1].split("?")[0]
        u = f"https://www.youtube.com/watch?v={video_id}"

    if "instagram.com" in u:
        u = u.split("?")[0]

    return u

def get_youtube_title(url: str):
    try:
        clean = fix_youtube_url(url)
        r = requests.get(
            f"https://www.youtube.com/oembed?url={clean}&format=json",
            timeout=5
        )
        r.raise_for_status()
        return r.json().get("title")
    except Exception:
        return None

# =========================================================
# 6) الهيدر + اللوغو
# =========================================================
@st.cache_data(ttl=60)
def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = None
for f in ["zain_logo_new.png", "zain_logo.png"]:
    if os.path.exists(f):
        logo = f
        break

if logo:
    st.markdown(f"""
    <div style="text-align:center">
        <img src="data:image/png;base64,{img_to_b64(logo)}" width="160">
        <h1>مكتبة زين</h1>
        <p>مساحتك الخاصة للإبداع</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("مكتبة زين")

# =========================================================
# 7) إضافة فيديو
# =========================================================
with st.expander("➕ إضافة فيديو جديد"):
    url = st.text_input("رابط الفيديو")

    if st.button("جلب العنوان 🔍"):
        title = get_youtube_title(url)
        if title:
            st.session_state.temp_title = title
            st.success("تم جلب العنوان")
        else:
            st.warning("لم يتم العثور على العنوان")

    title_in = st.text_input("العنوان", value=st.session_state.get("temp_title", ""))
    cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])

    if st.button("حفظ ✅"):
        final_url = fix_youtube_url(url)

        if not title_in or not final_url:
            st.error("البيانات غير مكتملة")
        elif any(v["path"] == final_url for v in st.session_state.videos):
            st.warning("هذا الفيديو مضاف مسبقًا")
        else:
            st.session_state.videos.append({
                "title": title_in,
                "path": final_url,
                "category": cat_in,
                "date": time.strftime("%Y-%m-%d")
            })
            save_to_disk()
            st.session_state.pop("temp_title", None)
            st.rerun()

# =========================================================
# 8) العرض
# =========================================================
st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

def show_video(item):
    key = f"{item['date']}_{hash(item['path'])}"

    with st.expander(f"🎥 {item['title']}"):
        st.video(item["path"])
        st_copy_to_clipboard(item["path"], "نسخ الرابط 📋", key=f"copy_{key}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<a class="dl-link savefrom-btn" href="https://en.savefrom.net/" target="_blank">SaveFrom</a>', unsafe_allow_html=True)
        with c2:
            st.markdown('<a class="dl-link cobalt-btn" href="https://cobalt.tools" target="_blank">Cobalt</a>', unsafe_allow_html=True)

        st.caption(f"تاريخ الإضافة: {item['date']}")

        if st.button("حذف 🗑️", key=f"del_{key}"):
            idx = st.session_state.videos.index(item)
            st.session_state.videos.pop(idx)
            save_to_disk()
            st.rerun()

for i, cat in enumerate(categories):
    with tabs[i]:
        vids = [
            v for v in reversed(st.session_state.videos)
            if cat == "الكل" or v["category"] == cat
        ]
        if not vids:
            st.info("لا يوجد محتوى")
        for v in vids:
            show_video(v)
