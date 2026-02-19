import streamlit as st
import json
import os
import time
import base64
import requests
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مكتبة زين", page_icon="📚", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 🛑 إعدادات قاعدة البيانات السحابية (JSONBin) 🛑
# ==========================================
JSONBIN_BIN_ID = ""  # ضع الـ ID هنا
JSONBIN_API_KEY = "" # ضع الـ API Key هنا
# ==========================================

# --- 2. دوال مساعدة ---
def toggle_theme():
    st.session_state.theme_mode = 'light' if st.session_state.theme_mode == 'dark' else 'dark'

@st.cache_data
def get_img_as_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

@st.cache_data
def get_active_logo(mode):
    candidates = ["zain_logo.webp", "zain_logo_new.png", "zain_logo.png", "zain_logo.jpg"] if mode == 'dark' else ["zain_logo_dark.webp", "zain_logo_dark.jpg", "zain_logo_dark.png"]
    for path in candidates:
        if os.path.exists(path): return path
    return None

# --- 3. إدارة الوضع والتصميم ---
if 'theme_mode' not in st.session_state: st.session_state.theme_mode = 'dark'
col_mode, _ = st.columns([0.1, 0.9])
with col_mode: st.button("🌓", on_click=toggle_theme, help="تبديل الوضع")

vars = {
    "bg": "#0f172a", "text": "#ffffff", "grad": "radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%)",
    "inp_bg": "#1e293b", "inp_text": "#ffffff", "head": "rgba(30, 41, 59, 0.7)", "btn_bg": "#0ea5e9", "btn_text": "#ffffff"
} if st.session_state.theme_mode == 'dark' else {
    "bg": "#f8fafc", "text": "#1e293b", "grad": "radial-gradient(circle at 50% 0%, #e2e8f0 0%, #f8fafc 70%)",
    "inp_bg": "#ffffff", "inp_text": "#1e293b", "head": "rgba(226, 232, 240, 0.8)", "btn_bg": "#3b82f6", "btn_text": "#ffffff"
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&display=swap');
    html, body, .stApp {{ background-color: {vars['bg']} !important; background-image: {vars['grad']}; background-attachment: fixed; color: {vars['text']} !important; }}
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown p {{ font-family: 'Almarai', sans-serif !important; color: {vars['text']} !important; }}
    [data-testid="stExpanderToggleIcon"], svg {{ display: none !important; visibility: hidden !important; }}
    .stTextInput input, div[data-baseweb="select"] > div {{ background-color: {vars['inp_bg']} !important; color: {vars['inp_text']} !important; border: 1px solid rgba(128, 128, 128, 0.4) !important; direction: rtl !important; text-align: right !important; -webkit-text-fill-color: {vars['inp_text']} !important; font-family: 'Almarai', sans-serif !important; }}
    .stButton button {{ background-color: {vars['btn_bg']} !important; color: {vars['btn_text']} !important; border: none !important; border-radius: 8px !important; font-family: 'Almarai', sans-serif !important; }}
    .stButton button p {{ color: {vars['btn_text']} !important; font-weight: bold !important; }}
    .streamlit-expanderHeader {{ background-color: {vars['head']} !important; border-radius: 15px !important; padding: 15px 20px !important; margin-bottom: 12px; display: block !important; border: none !important; }}
    .streamlit-expanderHeader p {{ font-size: 1.1rem !important; font-weight: 700 !important; margin: 0 !important; text-align: right !important; width: 100% !important; direction: rtl !important; }}
    .center-logo {{ display: block; margin-left: auto; margin-right: auto; width: 130px; height: auto; }}
    #MainMenu, footer, header {{visibility: hidden;}}
    .dl-link {{ display: block; width: 100%; padding: 12px 5px; margin: 5px 0; text-align: center; border-radius: 8px; text-decoration: none !important; font-weight: 700; color: white !important; font-size: 0.95rem; }}
    .savefrom-btn {{ background: linear-gradient(135deg, #10b981, #059669); }}
    .y2mate-btn {{ background: linear-gradient(135deg, #8b5cf6, #6d28d9); }}
    .cobalt-btn {{ background: linear-gradient(135deg, #3b82f6, #2563eb); }}
    </style>
""", unsafe_allow_html=True)

logo_path = get_active_logo(st.session_state.theme_mode)
if logo_path:
    img_b64 = get_img_as_base64(logo_path)
    mime = "image/webp" if logo_path.endswith("webp") else f"image/{logo_path.split('.')[-1].replace('jpg', 'jpeg')}"
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="data:{mime};base64,{img_b64}" class="center-logo">
            <h1 style="margin-top: 10px; font-size: 3rem; color: {vars['text']}; text-shadow: 0 0 20px rgba(56, 189, 248, 0.3);">مكتبة زين</h1>
        </div>
    """, unsafe_allow_html=True)

# --- 4. إدارة البيانات السحابية ---
def load_data():
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try:
            res = requests.get(f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest", headers={"X-Master-Key": JSONBIN_API_KEY}, timeout=5)
            if res.status_code == 200: return res.json().get('record', [])
        except: pass
    if os.path.exists("zain_library.json"):
        try: return json.load(open("zain_library.json", "r", encoding="utf-8"))
        except: return []
    return []

def save_data(data):
    if JSONBIN_BIN_ID and JSONBIN_API_KEY:
        try: requests.put(f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}", json=data, headers={"Content-Type": "application/json", "X-Master-Key": JSONBIN_API_KEY}, timeout=5)
        except: pass
    with open("zain_library.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'videos' not in st.session_state:
    st.session_state.videos = load_data()

def fix_url(url):
    u = url.strip()
    if "youtube.com/shorts/" in u: return f"https://www.youtube.com/watch?v={u.split('shorts/')[-1].split('?')[0]}"
    if "youtu.be/" in u: return f"https://www.youtube.com/watch?v={u.split('youtu.be/')[-1].split('?')[0]}"
    return u

def extract_video_id(url):
    if "watch?v=" in url: return url.split("watch?v=")[-1].split("&")[0]
    return ""

def get_youtube_title(url):
    try:
        clean = fix_url(url)
        res = requests.get(f"https://www.youtube.com/oembed?url={clean}&format=json", timeout=3)
        if res.status_code == 200: return res.json().get('title')
    except: pass
    return None

# --- 5. الإدخال (مع جلب العنوان التلقائي المصلح) ---
with st.expander("➕ إضافة فيديو جديد", expanded=False):
    url_in = st.text_input("رابط الفيديو (يوتيوب أو إنستغرام)")
    
    # عودة زر جلب العنوان للحياة
    if st.button("🔍 جلب العنوان"):
        if url_in:
            t = get_youtube_title(url_in)
            if t:
                st.session_state.temp_title = t
                st.success("تم جلب العنوان بنجاح!")
            else:
                st.warning("لم أتمكن من جلب العنوان. إذا كان الرابط لإنستغرام، يرجى كتابته يدوياً.")
    
    dt = st.session_state.get('temp_title', '')
    c1, c2 = st.columns([1, 1])
    with c2: title_in = st.text_input("العنوان", value=dt)
    with c1: cat_in = st.selectbox("التصنيف", ["دراسة", "ديني", "تصميم", "ترفيه", "أخرى"])
    
    if st.button("حفظ الفيديو ✅"):
        if title_in and url_in:
            st.session_state.videos.append({
                "title": title_in, "path": fix_url(url_in), "category": cat_in, "date": time.strftime("%Y-%m-%d")
            })
            save_data(st.session_state.videos)
            if 'temp_title' in st.session_state: del st.session_state.temp_title
            st.rerun()

st.markdown("---")
categories = ["الكل", "دراسة", "ديني", "تصميم", "ترفيه", "أخرى"]
tabs = st.tabs(categories)

# --- 6. العرض والتحميل ---
VIDEOS_PER_PAGE = 5 
if 'page_num' not in st.session_state: st.session_state.page_num = 0

for i, cat in enumerate(categories):
    with tabs[i]:
        all_items = [v for v in reversed(st.session_state.videos) if cat == "الكل" or v['category'] == cat]
        if not all_items:
            st.info("لا يوجد محتوى")
        else:
            total_pages = max(1, (len(all_items) + VIDEOS_PER_PAGE - 1) // VIDEOS_PER_PAGE)
            current_page = min(max(0, st.session_state.page_num), total_pages - 1)
            page_items = all_items[current_page * VIDEOS_PER_PAGE : (current_page + 1) * VIDEOS_PER_PAGE]
            
            for idx, vid in enumerate(page_items):
                unique_key = f"{cat}_{current_page * VIDEOS_PER_PAGE + idx}"
                is_ig = "instagram.com" in vid['path']
                
                with st.expander(f"🎥 {vid['title']}"):
                    if is_ig:
                        st.info("📱 مقطع إنستغرام (تفضل بالتحميل المباشر من الأسفل)")
                        st.markdown(f"**[🔗 الرابط الأصلي على إنستغرام]({vid['path']})**")
                    else:
                        st.video(vid['path'])
                    
                    st_copy_to_clipboard(vid['path'], "📋 نسخ الرابط", key=f"cp_{unique_key}")
                    
                    # هندسة الأزرار حسب نوع الرابط
                    if is_ig:
                        # إنستغرام: فقط زر كوبات الصافي والمضمون
                        st.markdown('<a href="https://cobalt.tools" target="_blank" class="dl-link cobalt-btn">💎 أداة Cobalt (لتحميل إنستغرام)</a>', unsafe_allow_html=True)
                    else:
                        # يوتيوب: زر للفيديو السريع، وزر للمقاطع الطويلة والصوتيات
                        c1, c2 = st.columns(2)
                        ss_url = vid['path'].replace("youtube.com", "ssyoutube.com")
                        vid_id = extract_video_id(vid['path'])
                        y2meta_url = f"https://y2meta.app/youtube/{vid_id}" if vid_id else "https://y2meta.app"
                        
                        c1.markdown(f'<a href="{ss_url}" target="_blank" class="dl-link savefrom-btn">🟢 تحميل فيديو (SS)</a>', unsafe_allow_html=True)
                        c2.markdown(f'<a href="{y2meta_url}" target="_blank" class="dl-link y2mate-btn">🚀 يوتيوب شامل + صوت (Y2Meta)</a>', unsafe_allow_html=True)
                    
                    if st.button("حذف 🗑️", key=f"del_{unique_key}"):
                        st.session_state.videos.remove(vid)
                        save_data(st.session_state.videos)
                        st.rerun()
            
            st.markdown("---")
            c_prev, c_info, c_next = st.columns([1, 2, 1])
            with c_prev:
                if current_page > 0 and st.button("السابق ⬅️", key=f"prev_{cat}"):
                    st.session_state.page_num -= 1; st.rerun()
            with c_info: st.markdown(f"<div style='text-align: center;'>صفحة {current_page + 1} من {total_pages}</div>", unsafe_allow_html=True)
            with c_next:
                if current_page < total_pages - 1 and st.button("التالي ➡️", key=f"next_{cat}"):
                    st.session_state.page_num += 1; st.rerun()
