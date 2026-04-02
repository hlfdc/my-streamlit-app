import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

# ====================== 页面配置（微信极致体验） ======================
st.set_page_config(
    page_title="生活小管家",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ====================== 开屏动画（APP启动页） ======================
if "first_load" not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    splash = st.empty()
    splash.markdown("""
        <div style="height: 100vh; display: flex; justify-content: center; align-items: center; flex-direction: column; background: #f5f7fa;">
            <div style="font-size: 40px;">🏠</div>
            <div style="font-size: 24px; font-weight: 700; margin-top: 20px;">生活小管家</div>
            <div style="font-size: 14px; color: #888; margin-top: 10px;">AI 生活助手 · 启动中...</div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.2)
    splash.empty()
    st.session_state.first_load = False

# ====================== 全局CSS（小程序级UI） ======================
st.markdown("""
<style>
body {
    background: #f5f7fa !important;
    max-width: 480px !important;
    margin: 0 auto !important;
    padding-bottom: 30px !important;
}
.block-container {
    padding: 0 16px !important;
    max-width: 480px !important;
}
/* 卡片 */
.card {
    background: #ffffff;
    border-radius: 22px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.05);
}
/* 标题 */
.title {
    font-size: 29px;
    font-weight: 800;
    color: #111;
    margin-bottom: 6px;
}
.subtitle {
    font-size: 15px;
    color: #777;
    margin-bottom: 24px;
}
/* 按钮 */
.stButton>button {
    width: 100% !important;
    border-radius: 20px !important;
    background: #3E63F6 !important;
    color: white !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 17px !important;
    border: none !important;
}
.stButton>button:active {
    background: #2E4AE0 !important;
}
/* 输入框 */
.stTextInput>div>div, .stNumberInput>div>div, .stSelectbox>div>div {
    border-radius: 18px !important;
    height: 54px !important;
    font-size: 15px !important;
}
/* 一键复制按钮 */
.copy-btn {
    background: #f0f4ff;
    color: #3E63F6;
    border-radius: 12px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: inline-block;
    margin-top: 8px;
}
/* 隐藏所有垃圾元素 */
#MainMenu, footer, header, .stDeployButton, div[data-testid="stStatusWidget"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ====================== 底部TAB ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 首页", "🍳 菜谱", "🛠️ 妙招", "📦 食材", "📜 历史"
])

# ====================== AI配置（你真实可用） ======================
API_KEY = "171a9a59-d91c-4716-899a-29ff6688de57"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "ep-20260402064205-f588x"

SYSTEM_PROMPT = """
你是【生活小管家】，专业、贴心、步骤简单、安全家用。
只回答：菜谱、清洁、收纳、衣物洗护、食材消耗。
语言简洁清晰，不废话，实用为主。
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
        "temperature": 0.4,
        "max_tokens": 2000
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data, timeout=45)
        res_json = resp.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"]
        else:
            return "⚠️ 服务繁忙，请重试"
    except:
        return "❌ 网络异常，请检查后重试"

# ====================== 历史 ======================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(typ, q, a):
    st.session_state.history.append({"type": typ, "q": q, "a": a})

# ====================== 导出/复制 ======================
def text_to_file(text, fn):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{fn}" style="color:#3E63F6; text-decoration:none;">📄 保存文本</a>'

def copy_btn(text):
    return f'''
        <div class="copy-btn" onclick="navigator.clipboard.writeText(`{text.replace('`','')}`)">
            📋 一键复制回答
        </div>
    '''

# ====================== 首页 ======================
with tab1:
    st.markdown('<div class="title">🏠 生活小管家</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">你的AI全能生活助手</div>', unsafe_allow_html=True)

    for title, desc in [
        ("🍳 菜谱生成", "家里有啥做啥"),
        ("🛠️ 生活妙招", "清洁去污收纳技巧"),
        ("📦 食材消耗", "临期食材不浪费"),
    ]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {title}")
        st.caption(desc)
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
            with st.spinner("正在生成..."):
                q = f"食材{ing}，{num}人，{tm}，2个家常菜，偏好{pref}"
                a = chat(q)
                st.session_state.res = a
                st.markdown(a)
                st.markdown(copy_btn(a), unsafe_allow_html=True)
                add_history("菜谱", q, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"菜谱.txt"),unsafe_allow_html=True)

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
                st.markdown(copy_btn(a), unsafe_allow_html=True)
                add_history("妙招", q, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"妙招.txt"),unsafe_allow_html=True)

# ====================== 食材消耗 ======================
with tab4:
    st.markdown('<div class="title">📦 食材消耗</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    s = st.text_input("临期食材")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("✅ 生成消耗菜谱"):
        if s:
            with st.spinner("生成中..."):
                a = chat(f"用{s}做家常菜，简单好吃不浪费")
                st.session_state.res = a
                st.markdown(a)
                st.markdown(copy_btn(a), unsafe_allow_html=True)
                add_history("食材", s, a)
    if "res" in st.session_state:
        c1,c2 = st.columns(2)
        c1.markdown(text_to_file(st.session_state.res,"消耗菜谱.txt"),unsafe_allow_html=True)

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
                st.markdown(copy_btn(i['a']), unsafe_allow_html=True)
