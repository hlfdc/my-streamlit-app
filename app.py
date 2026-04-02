import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

# ====================== 页面配置（手机APP风格） ======================
st.set_page_config(
    page_title="生活小管家",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ====================== 📱 手机APP美化CSS ======================
st.markdown("""
<style>
body {
    background-color: #f2f5f7 !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}
.block-container {
    padding: 0 12px !important;
    max-width: 480px !important;
}
.card {
    background: #ffffff;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
.title {
    font-size: 26px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 8px;
}
.subtitle {
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 20px;
}
.stButton>button {
    width: 100% !important;
    border-radius: 16px !important;
    background-color: #4A7DFF !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 14px !important;
    border: none !important;
}
.stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div {
    border-radius: 16px !important;
    height: 50px !important;
}
section[data-testid="stSidebar"], #MainMenu, footer, header {
    display: none !important;
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# ====================== 底部TAB ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 首页", "🍳 菜谱", "🛠️ 妙招", "📦 食材", "📜 历史"
])

# ====================== ✅ 你的正确AI配置 ======================
API_KEY = "171a9a59-d91c-4716-899a-29ff6688de57"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "doubao-seed-1.6-flash-4k"

SYSTEM_PROMPT = """
你是【生活小管家智能体】，专业、贴心、实用。
只回答生活相关：菜谱、清洁去污、衣物洗护、收纳、食材消耗、家务规划。
语言通俗、步骤简单、安全家用，不回答无关内容。
"""

# ====================== AI聊天函数 ======================
def chat(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data, timeout=30)
        res_json = resp.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"]
        else:
            return "⚠️ AI返回异常，请重试"
    except Exception as e:
        return f"❌ 连接失败：{str(e)}"

# ====================== 历史记录 ======================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(typ, q, a):
    st.session_state.history.append({"type": typ, "q": q, "a": a})

# ====================== 导出 ======================
def text_to_file(text, fn):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{fn}" style="color:#4A7DFF; text-decoration:none;">📄 保存文本</a>'

def text_to_image(text):
    lines = textwrap.wrap(text, 42)
    h = min(1000, 80 + len(lines)*26)
    im = Image.new("RGB", (600, h), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.load_default(size=18)
    y = 25
    for l in lines:
        d.text((25, y), l, fill="#111", font=f)
        y += 26
    buf = BytesIO()
    im.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ====================== 首页（已修复###问题） ======================
with tab1:
    st.markdown('<div class="title">🏠 生活小管家</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">你的AI生活助手</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🍳 菜谱生成")
    st.caption("家里有啥做啥")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ 生活妙招")
    st.caption("清洁、去污、收纳")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📦 食材消耗")
    st.caption("临期食材不浪费")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 菜谱 ======================
with tab2:
    st.markdown('<div class="title">🍳 菜谱生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    ing = st.text_input("现有食材")
    pref = st.text_input("偏好/忌口")
    c1,c2 = st.columns(2)
    with c1: num = st.number_input("人数",1,10,2)
    with c2: tm = st.selectbox("用时",["10分钟","20分钟","30分钟"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✅ 生成菜谱"):
        if ing:
            with st.spinner("生成中..."):
                q = f"食材{ing}，偏好{pref}，{num}人，{tm}，2个家常菜"
                a = chat(q)
                st.session_state.res = a
                st.markdown(a)
                add_history("菜谱", q, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"菜谱.txt"),unsafe_allow_html=True)
        c2.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="菜谱.png" style="color:#4A7DFF; text-decoration:none;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 妙招 ======================
with tab3:
    st.markdown('<div class="title">🛠️ 生活妙招</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    q = st.text_input("你想解决什么问题？")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ 获取方法"):
        if q:
            with st.spinner("查找中..."):
                a = chat(f"生活问题：{q}，家用简单安全方法")
                st.session_state.res = a
                st.markdown(a)
                add_history("妙招", q, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"妙招.txt"),unsafe_allow_html=True)
        c2.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="妙招.png" style="color:#4A7DFF; text-decoration:none;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 食材消耗 ======================
with tab4:
    st.markdown('<div class="title">📦 食材消耗</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    s = st.text_input("临期食材")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ 生成消耗菜谱"):
        if s:
            with st.spinner("生成中..."):
                a = chat(f"用食材{s}做家常菜，不浪费")
                st.session_state.res = a
                st.markdown(a)
                add_history("食材", s, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"消耗菜谱.txt"),unsafe_allow_html=True)
        c2.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="消耗菜谱.png" style="color:#4A7DFF; text-decoration:none;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 历史 ======================
with tab5:
    st.markdown('<div class="title">📜 历史记录</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("暂无记录")
    else:
        for i in reversed(st.session_state.history):
            with st.expander(f"【{i['type']}】{i['q'][:25]}..."):
                st.write("问题：", i['q'])
                st.markdown(i['a'])
