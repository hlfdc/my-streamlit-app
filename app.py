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

# ====================== 页面配置（必须第一行） ======================
st.set_page_config(
    page_title="生活小管家智能体",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== ✅ 完整版 CSS 美化（盒子 + 按钮 + 卡片 + 隐藏水印） ======================
st.markdown("""
<style>
    /* 全局布局 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    /* 主标题 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* 卡片盒子（你要的 CSS 盒子在这里！） */
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
        margin-bottom: 18px;
    }

    /* 按钮美化 */
    .stButton>button {
        background-color: #2563EB !important;
        color: white !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        padding: 10px 25px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
    }

    /* 隐藏 Streamlit 水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ====================== 豆包 API ======================
API_KEY = os.getenv("DOUBAO_API_KEY")
BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

SYSTEM_PROMPT = """
你是【生活小管家智能体】，专业、贴心、实用。
只回答生活相关：菜谱、清洁去污、衣物洗护、收纳、食材消耗、家务规划。
语言通俗、步骤简单、安全家用，不回答无关内容。
"""

def chat(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "doubao-lite",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 调用失败：{str(e)}"

# ====================== 历史记录 ======================
if "history" not in st.session_state:
    st.session_state.history = []

def add_history(typ, question, answer):
    st.session_state.history.append({
        "type": typ,
        "q": question,
        "a": answer
    })

# ====================== 侧边栏 ======================
with st.sidebar:
    st.title("🏠 生活小管家")
    st.markdown("---")
    menu = st.radio("菜单", [
        "🏠 首页",
        "🍳 菜谱生成",
        "🛠️ 生活妙招",
        "📦 食材消耗",
        "📜 历史记录",
        "ℹ️ 关于"
    ])
    st.markdown("---")
    if st.button("清空历史记录"):
        st.session_state.history = []
        st.success("已清空")

# ====================== 语音输入 ======================
def speech_input(label):
    audio = mic_recorder(start_prompt="🎤 说话", stop_prompt="⏹ 停止", just_once=True)
    text = ""
    if audio and audio.get("text"):
        text = audio["text"]
    return st.text_input(label, value=text)

# ====================== 导出 ======================
def text_to_file(text, filename="结果.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}">📄 下载文本</a>'

def text_to_image(text, width=600):
    lines = textwrap.wrap(text, width=45)
    height = min(1200, 80 + len(lines)*28)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black", font=font)
        y += 28
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# ====================== 🏠 首页（已加卡片） ======================
if menu == "🏠 首页":
    st.markdown('<h1 class="main-title">🏠 生活小管家智能体</h1>', unsafe_allow_html=True)
    st.subheader("你的随身生活帮手，说话就能用 ✅")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🍳 菜谱生成")
        st.write("家里有啥做啥，减脂/快手/家常")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🛠️ 生活妙招")
        st.write("清洁、去污、洗护、收纳")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📦 食材消耗")
        st.write("清空冰箱，不浪费粮食")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🌟 使用说明")
    st.write("1. 选择功能 → 2. 语音/文字输入 → 3. 一键生成 → 4. 可导出图片")
    st.info("支持语音输入，做饭、打扫时解放双手！")

# ====================== 🍳 菜谱 ======================
elif menu == "🍳 菜谱生成":
    st.markdown('<h1 class="main-title">🍳 个性化菜谱</h1>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        ingredients = speech_input("现有食材（逗号分隔）")
        preference = st.text_input("偏好/忌口", placeholder="减脂、不吃辣、素食...")
    with col2:
        people = st.number_input("用餐人数", 1, 10, 2)
        max_time = st.selectbox("最长用时", ["10分钟", "20分钟", "30分钟", "不限"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✅ 生成菜谱", use_container_width=True):
        if not ingredients:
            st.warning("请输入至少一种食材")
        else:
            q = f"食材：{ingredients}，偏好：{preference}，{people}人，{max_time}"
            with st.spinner("正在生成..."):
                ans = chat(f"生成2个家常菜谱：{q}")
                st.session_state.current_result = ans
                st.markdown(ans)
                add_history("菜谱", q, ans)

    if "current_result" in st.session_state:
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(text_to_file(st.session_state.current_result, "菜谱.txt"), unsafe_allow_html=True)
        with c2:
            imgb64 = text_to_image(st.session_state.current_result)
            st.markdown(f'<a href="data:image/png;base64,{imgb64}" download="菜谱.png">🖼️ 下载图片</a>', unsafe_allow_html=True)

# ====================== 🛠️ 生活妙招 ======================
elif menu == "🛠️ 生活妙招":
    st.markdown('<h1 class="main-title">🛠️ 生活小妙招</h1>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    question = speech_input("你想解决什么问题？")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("✅ 获取方法", use_container_width=True):
        if question:
            with st.spinner("正在查找..."):
                ans = chat(f"生活问题：{question}，家用简单方法")
                st.session_state.current_result = ans
                st.markdown(ans)
                add_history("生活妙招", question, ans)
        else:
            st.warning("请输入问题")

    if "current_result" in st.session_state:
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(text_to_file(st.session_state.current_result, "妙招.txt"), unsafe_allow_html=True)
        with c2:
            imgb64 = text_to_image(st.session_state.current_result)
            st.markdown(f'<a href="data:image/png;base64,{imgb64}" download="妙招.png">🖼️ 下载图片</a>', unsafe_allow_html=True)

# ====================== 📦 食材消耗 ======================
elif menu == "📦 食材消耗":
    st.markdown('<h1 class="main-title">📦 临期食材消耗</h1>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    stock = speech_input("输入快过期的食材（可语音）")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("✅ 生成不浪费菜谱", use_container_width=True):
        if stock:
            q = f"快过期食材：{stock}"
            with st.spinner("正在生成..."):
                ans = chat(f"用这些食材做家常菜：{stock}")
                st.session_state.current_result = ans
                st.markdown(ans)
                add_history("食材消耗", q, ans)
        else:
            st.warning("请输入食材")

    if "current_result" in st.session_state:
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(text_to_file(st.session_state.current_result, "消耗菜谱.txt"), unsafe_allow_html=True)
        with c2:
            imgb64 = text_to_image(st.session_state.current_result)
            st.markdown(f'<a href="data:image/png;base64,{imgb64}" download="消耗菜谱.png">🖼️ 下载图片</a>', unsafe_allow_html=True)

# ====================== 📜 历史 ======================
elif menu == "📜 历史记录":
    st.title("📜 历史记录")
    if not st.session_state.history:
        st.info("暂无记录")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"【{item['type']}】{item['q'][:30]}..."):
                st.markdown("**问题**")
                st.write(item["q"])
                st.markdown("**回答**")
                st.markdown(item["a"])

# ====================== ℹ️ 关于 ======================
elif menu == "ℹ️ 关于":
    st.title("ℹ️ 关于生活小管家")
    st.markdown("### 🏠 产品介绍")
    st.write("一款基于AI的生活服务智能体，专注解决日常饮食、清洁、收纳、家务问题。")
    st.markdown("### ✨ 核心功能")
    st.write("- 个性化菜谱生成")
    st.write("- 生活妙招问答")
    st.write("- 临期食材消耗")
    st.write("- 语音输入、导出图片")
    st.markdown("---")
    st.markdown("📌 本项目由AI智能体开发 | 可用于学习、副业、工具引流")

# ====================== 底部 ======================
st.markdown("---")
st.caption("© 2026 生活小管家智能体 | 仅供个人使用")