import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from pdf_reader import extract_text_from_pdf

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMind — AI Study Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ──────────────────────────────────────── */
:root {
    --bg-primary:    #0f0f1a;
    --bg-secondary:  #1a1a2e;
    --bg-card:       rgba(30, 30, 55, 0.65);
    --accent:        #7c3aed;
    --accent-light:  #a78bfa;
    --accent-glow:   rgba(124, 58, 237, 0.35);
    --text-primary:  #f1f1f6;
    --text-secondary:#a0a0b8;
    --border:        rgba(255,255,255,0.06);
    --success:       #34d399;
}

/* ── Global ──────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #16162a 0%, #1e1e3a 100%) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* ── Hero Title ──────────────────────────────────────────── */
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0;
    letter-spacing: -1px;
    animation: fadeSlideDown 0.8s ease-out;
}
.hero-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1.05rem;
    font-weight: 400;
    margin-top: 0;
    margin-bottom: 2rem;
    animation: fadeSlideDown 1s ease-out;
}

/* ── Glass Card ──────────────────────────────────────────── */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(124,58,237,0.15);
}
.glass-card h3 {
    margin-top: 0;
    color: var(--accent-light);
    font-weight: 600;
}

/* ── Stat Pill ───────────────────────────────────────────── */
.stat-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1rem 0 0.5rem;
}
.stat-pill {
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 999px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
    color: var(--accent-light);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Answer Box ──────────────────────────────────────────── */
.answer-box {
    background: linear-gradient(135deg, rgba(124,58,237,0.08) 0%, rgba(6,182,212,0.06) 100%);
    border-left: 4px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
    color: var(--text-primary);
    line-height: 1.75;
    font-size: 1rem;
}
.answer-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    color: var(--accent-light);
    margin-bottom: 0.6rem;
    font-size: 1rem;
}

/* ── Question Bubble ─────────────────────────────────────── */
.question-bubble {
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.8rem;
    color: var(--text-primary);
    font-size: 0.95rem;
}
.question-bubble .q-label {
    color: var(--text-secondary);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.3rem;
}

/* ── File Uploader Styling ───────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(124,58,237,0.35) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    transition: border-color 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Input Styling ───────────────────────────────────────── */
[data-testid="stTextInput"] input {
    background: var(--bg-secondary) !important;
    border: 1px solid rgba(124,58,237,0.3) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
    font-size: 1rem !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
[data-testid="stTextInput"] label {
    color: var(--text-secondary) !important;
}

/* ── Button ──────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    cursor: pointer;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px var(--accent-glow) !important;
}

/* ── Spinner ─────────────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--accent-light) !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb {
    background: var(--accent);
    border-radius: 3px;
}

/* ── Animations ──────────────────────────────────────────── */
@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.6; }
}
.loading-dot {
    animation: pulse 1.2s infinite;
}

/* ── Sidebar brand ───────────────────────────────────────── */
.sidebar-brand {
    text-align: center;
    padding: 1.5rem 0 1rem;
}
.sidebar-brand .logo {
    font-size: 2.4rem;
    margin-bottom: 0.3rem;
}
.sidebar-brand .name {
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-brand .tagline {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1rem 0;
}

/* ── Feature list ────────────────────────────────────────── */
.feature-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0;
    color: var(--text-secondary);
    font-size: 0.88rem;
}
.feature-item .icon {
    font-size: 1.1rem;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── Upload area empty state ─────────────────────────────── */
.upload-prompt {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-secondary);
}
.upload-prompt .icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}
.upload-prompt p {
    font-size: 1.05rem;
    max-width: 360px;
    margin: 0 auto;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Initialize Session State ─────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# ── Gemini Client ─────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="logo">🧠</div>
        <div class="name">StudyMind</div>
        <div class="tagline">Your AI-Powered Study Partner</div>
    </div>
    <hr class="sidebar-divider">
    """, unsafe_allow_html=True)

    st.markdown("#### 📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Drop your PDF here",
        type="pdf",
        label_visibility="collapsed",
    )

    if uploaded_file:
        if uploaded_file.name != st.session_state.doc_name:
            st.session_state.doc_text = extract_text_from_pdf(uploaded_file)
            st.session_state.doc_name = uploaded_file.name
            st.session_state.history = []

        text = st.session_state.doc_text
        word_count = len(text.split())
        char_count = len(text)
        page_est = max(1, word_count // 300)

        st.markdown(f"""
        <div class="glass-card" style="padding:1rem 1.2rem; margin-top:0.8rem;">
            <h3 style="font-size:0.95rem; margin-bottom:0.6rem;">✅ Document Loaded</h3>
            <div style="font-size:0.85rem; color:var(--text-secondary); word-break:break-all;">
                {uploaded_file.name}
            </div>
            <div class="stat-row">
                <div class="stat-pill">📄 ~{page_est} pages</div>
                <div class="stat-pill">📝 {word_count:,} words</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown("#### ✨ Features")
    st.markdown("""
    <div class="feature-item"><span class="icon">📚</span> Ask questions from any PDF</div>
    <div class="feature-item"><span class="icon">⚡</span> Powered by Google Gemini</div>
    <div class="feature-item"><span class="icon">🎯</span> Context-aware answers</div>
    <div class="feature-item"><span class="icon">💬</span> Conversation history</div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        if st.button("🗑️  Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# ── Main Content Area ────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">StudyMind</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Upload a document. Ask anything. Learn smarter.</p>', unsafe_allow_html=True)

if not uploaded_file:
    st.markdown("""
    <div class="glass-card">
        <div class="upload-prompt">
            <div class="icon">📂</div>
            <p>Upload a PDF document from the sidebar to get started.<br>
            <span style="color:var(--accent-light); font-weight:500;">StudyMind</span>
            will read it and answer any question you have.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align:center; min-height:160px;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📄</div>
            <h3 style="font-size:1rem;">Upload PDF</h3>
            <p style="color:var(--text-secondary); font-size:0.88rem;">
                Drop any study material — textbooks, notes, or research papers.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align:center; min-height:160px;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">💡</div>
            <h3 style="font-size:1rem;">Ask Questions</h3>
            <p style="color:var(--text-secondary); font-size:0.88rem;">
                Type any question and get accurate, contextual answers instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align:center; min-height:160px;">
            <div style="font-size:2rem; margin-bottom:0.5rem;">🚀</div>
            <h3 style="font-size:1rem;">Learn Faster</h3>
            <p style="color:var(--text-secondary); font-size:0.88rem;">
                Save hours of reading — let AI extract exactly what you need.
            </p>
        </div>
        """, unsafe_allow_html=True)

else:
    text = st.session_state.doc_text

    # ── Q&A History ──────────────────────────────────────────────────────────
    if st.session_state.history:
        st.markdown("""
        <div class="glass-card">
            <h3 style="font-size:1.1rem;">💬 Conversation</h3>
        """, unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.history):
            st.markdown(f"""
            <div class="question-bubble">
                <div class="q-label">You asked</div>
                {item["question"]}
            </div>
            <div class="answer-box">
                <div class="answer-label">🧠 StudyMind</div>
                {item["answer"]}
            </div>
            """, unsafe_allow_html=True)
            if i < len(st.session_state.history) - 1:
                st.markdown("<hr style='border:none; border-top:1px solid var(--border); margin:1rem 0;'>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Question Input ───────────────────────────────────────────────────────
    st.markdown("")  # spacer
    question = st.text_input(
        "Ask a question from the document",
        placeholder="e.g. What are the key concepts in Chapter 3?",
        label_visibility="collapsed",
    )

    col_btn, col_space = st.columns([1, 3])
    with col_btn:
        ask_clicked = st.button("🔍  Ask StudyMind", use_container_width=True)

    if ask_clicked and question:
        prompt = f"""You are StudyMind, a helpful AI study assistant. Answer the following question
using ONLY the provided study material. Be clear, well-structured, and helpful.
Use bullet points or numbered lists when appropriate.

Study Material:
{text}

Question:
{question}

Provide a thorough yet concise answer:"""

        with st.spinner("🧠 Thinking..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

        answer = response.text
        st.session_state.history.append({
            "question": question,
            "answer": answer,
        })
        st.rerun()

    elif ask_clicked and not question:
        st.warning("Please type a question first.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:3rem 0 1rem; color:var(--text-secondary); font-size:0.8rem;">
    Built with 🧠 StudyMind &nbsp;·&nbsp; Powered by Google Gemini &nbsp;·&nbsp; Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)