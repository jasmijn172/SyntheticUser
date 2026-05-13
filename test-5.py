"""
Data Justice Assistent — Streamlit App
Synthetic User als cognitieve agent met real-time bias/hallucinatie/inclusie tracking
Gebouwd met Groq API (llama-3.3-70b-versatile) + LangGraph-geïnspireerde validatieflow
"""

import streamlit as st
import json
import os
import time

st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

# chat rendering hier

st.markdown('</div>', unsafe_allow_html=True)
# ─────────────────────────────────────────────
# PAGINA CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Data Justice Assistent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Dark Navy stijl (Archive_4 ontwerp)
# ─────────────────────────────────────────────

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@600;700&display=swap');

/* =====================================================
   ROOT TOKENS
===================================================== */

:root{
    --bg:#08111F;
    --bg-soft:#0F1728;
    --panel:#111C31;
    --panel-2:#172338;
    --border:#24324A;
    --border-soft:rgba(255,255,255,.05);

    --text:#F3F7FF;
    --muted:#8EA0BF;

    --blue:#4C8DFF;
    --blue-soft:rgba(76,141,255,.12);

    --green:#1DB87A;
    --amber:#F59E0B;
    --red:#EF4444;

    --radius:16px;
}

/* =====================================================
   GLOBAL
===================================================== */

html, body, .stApp{
    background:
        radial-gradient(circle at top left, rgba(76,141,255,.08), transparent 30%),
        radial-gradient(circle at top right, rgba(76,141,255,.04), transparent 25%),
        var(--bg) !important;

    color:var(--text) !important;
    font-family:'Inter',sans-serif !important;
}

#MainMenu,
footer,
header{
    visibility:hidden;
}

.block-container{
    max-width:100% !important;
    padding:0 !important;
}

/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"]{
    background:rgba(15,23,40,.92) !important;
    backdrop-filter:blur(18px);
    border-right:1px solid var(--border);
    width:300px !important;
}

section[data-testid="stSidebar"] > div{
    padding-top:20px;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{
    font-family:'Sora',sans-serif !important;
    color:var(--text);
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label{
    color:var(--muted) !important;
}

/* =====================================================
   TOPBAR
===================================================== */

.topbar{
    height:72px;
    padding:0 28px;

    display:flex;
    align-items:center;

    background:rgba(11,18,32,.75);
    backdrop-filter:blur(20px);

    border-bottom:1px solid var(--border-soft);

    position:sticky;
    top:0;
    z-index:999;
}

.topbar-logo{
    display:flex;
    align-items:center;
    gap:12px;

    font-family:'Sora',sans-serif;
    font-weight:700;
    font-size:15px;
}

.topbar-project{
    font-size:18px;
    font-weight:700;
    color:var(--blue);
}

.topbar-sub{
    font-size:11px;
    color:var(--muted);
}

/* =====================================================
   CHAT LAYOUT
===================================================== */

.chat-shell{
    max-width:1100px;
    margin:auto;
    padding:32px 32px 140px 32px;
}

.msg-wrap-bot{
    display:flex;
    flex-direction:column;
    margin-bottom:24px;
}

.msg-wrap-user{
    display:flex;
    flex-direction:column;
    align-items:flex-end;
    margin-bottom:24px;
}

.msg-time{
    font-size:10px;
    color:var(--muted);
    margin-bottom:6px;
}

.msg-sender{
    font-size:11px;
    font-weight:600;
    color:#72A7FF;
    margin-bottom:7px;
}

/* =====================================================
   BUBBLES
===================================================== */

.bubble-bot{
    background:linear-gradient(
        180deg,
        rgba(23,35,56,.95),
        rgba(17,28,49,.95)
    );

    border:1px solid rgba(255,255,255,.05);

    border-radius:18px 18px 18px 6px;

    padding:18px 20px;

    max-width:780px;

    line-height:1.7;
    font-size:13px;

    box-shadow:
        0 8px 30px rgba(0,0,0,.22),
        inset 0 1px 0 rgba(255,255,255,.02);
}

.bubble-user{
    background:linear-gradient(
        180deg,
        #4C8DFF,
        #3777E8
    );

    border-radius:18px 18px 6px 18px;

    padding:18px 20px;

    max-width:720px;

    line-height:1.7;
    font-size:13px;

    color:white;

    box-shadow:
        0 10px 25px rgba(76,141,255,.22);
}

/* =====================================================
   PERSONA CARD
===================================================== */

.persona-card{
    background:
        linear-gradient(
            180deg,
            rgba(24,36,58,.96),
            rgba(17,28,49,.96)
        );

    border:1px solid rgba(255,255,255,.06);

    border-radius:22px;

    padding:24px;

    margin-top:18px;

    box-shadow:
        0 20px 50px rgba(0,0,0,.25);
}

.pc-name{
    font-family:'Sora',sans-serif;
    font-size:22px;
    font-weight:700;
}

.pc-diag{
    color:#6FA5FF;
    font-size:12px;
    margin-top:2px;
}

.pc-quote{
    color:var(--muted);
    font-style:italic;
    line-height:1.7;
    margin-top:14px;
}

.pc-tag{
    display:inline-flex;
    align-items:center;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.06);

    border-radius:999px;

    padding:5px 12px;

    font-size:11px;

    color:#A9B8D3;

    margin:5px 5px 0 0;
}

/* =====================================================
   XAI BOX
===================================================== */

.xai-box{
    margin-top:18px;

    background:rgba(10,17,31,.75);

    border:1px solid rgba(255,255,255,.05);

    border-radius:18px;

    padding:20px;

    backdrop-filter:blur(12px);
}

/* =====================================================
   RELIABILITY BAR
===================================================== */

.rel-bar{
    position:sticky;
    bottom:88px;
    z-index:90;

    margin:0 auto 24px auto;

    width:fit-content;

    display:flex;
    align-items:center;
    gap:10px;

    background:rgba(11,18,32,.92);

    border:1px solid rgba(255,255,255,.06);

    backdrop-filter:blur(16px);

    border-radius:999px;

    padding:12px 18px;

    box-shadow:
        0 10px 40px rgba(0,0,0,.35);
}

/* =====================================================
   BADGES
===================================================== */

.rel-badge-green,
.rel-badge-red,
.rel-badge-amber{
    border-radius:999px;
    padding:6px 12px;
    font-size:11px;
    font-weight:600;
}

.rel-badge-green{
    background:rgba(29,184,122,.12);
    border:1px solid rgba(29,184,122,.2);
    color:var(--green);
}

.rel-badge-amber{
    background:rgba(245,158,11,.12);
    border:1px solid rgba(245,158,11,.2);
    color:var(--amber);
}

.rel-badge-red{
    background:rgba(239,68,68,.12);
    border:1px solid rgba(239,68,68,.2);
    color:var(--red);
}

/* =====================================================
   INPUT AREA
===================================================== */

.stForm{
    position:fixed;
    bottom:0;
    left:300px;
    right:0;

    padding:20px 32px;

    background:
        linear-gradient(
            180deg,
            rgba(8,17,31,0),
            rgba(8,17,31,.95) 35%
        );

    backdrop-filter:blur(18px);

    z-index:999;
}

.stTextInput input{
    height:56px !important;

    background:rgba(17,28,49,.95) !important;

    border:1px solid rgba(255,255,255,.06) !important;

    border-radius:16px !important;

    color:white !important;

    padding:0 18px !important;

    font-size:14px !important;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.02);
}

.stTextInput input:focus{
    border:1px solid rgba(76,141,255,.45) !important;

    box-shadow:
        0 0 0 4px rgba(76,141,255,.08) !important;
}

/* =====================================================
   BUTTONS
===================================================== */

.stButton button{
    height:56px !important;

    border-radius:16px !important;

    border:none !important;

    background:
        linear-gradient(
            180deg,
            #4C8DFF,
            #3777E8
        ) !important;

    color:white !important;

    font-weight:600 !important;

    transition:.18s ease !important;

    box-shadow:
        0 8px 25px rgba(76,141,255,.25);
}

.stButton button:hover{
    transform:translateY(-1px);

    box-shadow:
        0 14px 32px rgba(76,141,255,.35);
}

/* =====================================================
   METRIC CARDS
===================================================== */

.metric-card{
    background:linear-gradient(
        180deg,
        rgba(20,30,48,.95),
        rgba(14,22,38,.95)
    );

    border:1px solid rgba(255,255,255,.05);

    border-radius:18px;

    padding:20px;

    text-align:center;

    box-shadow:
        0 10px 30px rgba(0,0,0,.2);
}

.metric-val{
    font-size:28px;
    font-weight:700;
}

.metric-lbl{
    margin-top:6px;
    font-size:11px;
    letter-spacing:.08em;
    text-transform:uppercase;
    color:var(--muted);
}

</style>
""", unsafe_allow_html=True)
