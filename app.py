import streamlit as st
import os
import requests
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

load_dotenv()

# ====================== 页面配置（手机APP必选） ======================
st.set_page_config(
    page_title="生活小管家",
    page_icon="🏠",
    layout="centered",  # 手机端必须 centered！
    initial_sidebar_state="collapsed"
)

# ====================== 📱 手机APP风格 CSS ======================
st.markdown("""
<style>
/* 全局手机APP样式 */
body {
    background-color: #f2f5f7 !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}
.block-container {
    padding: 0 12px !important;
    max-width: 480px !important;
}
/* 卡片：手机APP圆角 */
.card {
    background: #ffffff;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.04);
}
/* 标题：APP大标题 */
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
/* 按钮：APP质感 */
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
.stButton>button:active {
    background-color: #3562E6 !important;
}
/* 输入框圆角 */
.stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div {
    border-radius: 16px !important;
    height: 50px !important;
}
/* 隐藏侧边栏、水印、顶部导航 */
section[data-testid="stSidebar"] {display: none !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ====================== 底部 Tab 菜单（模拟APP底部栏） ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 首页", "🍳 菜谱", "🛠️ 妙招", "📦 食材", "📜 历史"
])

# ====================== API ======================
API_KEY = os.getenv("DOUBAO_API_KEY")
BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

SYSTEM_PROMPT = """
你是【生活小管家智能体】，专业、贴心、实用。
只回答生活相关：菜谱、清洁去污、衣物洗护、收纳、食材消耗、家务规划。
语言通俗、步骤简单、安全家用，不回答无关内容。
"""

def chat(prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "doubao-lite",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        "temperature": 0.6
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 调用失败：{str(e)}"

# ====================== 历史 ======================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(typ, question, answer):
    st.session_state.history.append({"type": typ, "q": question, "a": answer})

# ====================== 语音 & 导出 ======================
def speech_input(label):
    audio = mic_recorder(start_prompt="🎤 说话", stop_prompt="⏹ 停止", just_once=True)
    return st.text_input(label, value=audio["text"] if (audio and "text" in audio) else "")

def text_to_file(text, fn):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{fn}" style="text-decoration:none; color:#4A7DFF;">📄 保存文本</a>'

def text_to_image(text):
    lines = textwrap.wrap(text, 42)
    h = min(1000, 80 + len(lines)*26)
    im = Image.new("RGB", (600, h), "white")
    d = ImageDraw.Draw(im)
    f = ImageFont.load_default(size=18)
    y=25
    for l in lines:
        d.text((25,y), l, fill="#111", font=f)
        y+=26
    buf=BytesIO()
    im.save(buf,"PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ====================== 🏠 首页 ======================
with tab1:
    st.markdown('<div class="title">🏠 生活小管家</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">你的随身AI生活助手</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🍳 菜谱生成")
    st.caption("家里有啥做啥，不浪费")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ 生活妙招")
    st.caption("清洁、去污、收纳小技巧")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📦 食材消耗")
    st.caption("临期食材快速消耗")
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 🍳 菜谱 ======================
with tab2:
    st.markdown('<div class="title">🍳 菜谱生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    ing = speech_input("现有食材")
    pref = st.text_input("偏好/忌口", placeholder="减脂、不吃辣")
    col1,col2 = st.columns(2)
    with col1: num = st.number_input("人数",1,10,2)
    with col2: tm = st.selectbox("用时",["10分钟","20分钟","30分钟"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✅ 生成菜谱"):
        if ing:
            with st.spinner("生成中..."):
                q = f"食材{ing}，偏好{pref}，{num}人，{tm}，2个家常菜谱"
                a = chat(q)
                st.session_state.res = a
                st.markdown(a)
                add_history("菜谱",q,a)
    if "res" in st.session_state:
        c1,c2=st.columns(2)
        with c1: st.markdown(text_to_file(st.session_state.res,"菜谱.txt"),unsafe_allow_html=True)
        with c2: st.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="菜谱.png" style="color:#4A7DFF;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 🛠️ 妙招 ======================
with tab3:
    st.markdown('<div class="title">🛠️ 生活妙招</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    q = speech_input("你想解决什么问题？")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ 获取方法"):
        if q:
            with st.spinner("查找中..."):
                a=chat(f"生活问题：{q}，家用简单方法")
                st.session_state.res=a
                st.markdown(a)
                add_history("妙招",q,a)
    if "res" in st.session_state:
        c1,c2=st.columns(2)
        with c1: st.markdown(text_to_file(st.session_state.res,"妙招.txt"),unsafe_allow_html=True)
        with c2: st.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="妙招.png" style="color:#4A7DFF;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 📦 食材 ======================
with tab4:
    st.markdown('<div class="title">📦 食材消耗</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    s = speech_input("临期食材")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ 生成消耗菜谱"):
        if s:
            with st.spinner("生成中..."):
                q=f"临期食材{s}"
                a=chat(f"用{s}做家常菜")
                st.session_state.res=a
                st.markdown(a)
                add_history("食材",q,a)
    if "res" in st.session_state:
        c1,c2=st.columns(2)
        with c1: st.markdown(text_to_file(st.session_state.res,"消耗菜谱.txt"),unsafe_allow_html=True)
        with c2: st.markdown(f'<a href="data:image/png;base64,{text_to_image(st.session_state.res)}" download="消耗菜谱.png" style="color:#4A7DFF;">🖼️ 保存图片</a>',unsafe_allow_html=True)

# ====================== 📜 历史 ======================
with tab5:
    st.markdown('<div class="title">📜 历史记录</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.info("暂无记录")
    else:
        for i in reversed(st.session_state.history):
            with st.expander(f"【{i['type']}】{i['q'][:25]}..."):
                st.write("**问题**",i['q'])
                st.markdown(i['a'])
