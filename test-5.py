
# =========================================================
# ARCHIVE_4 STYLE — STREAMLIT FOUNDATION
# Complete drop-in UI layer
# =========================================================

import streamlit as st

st.set_page_config(
    page_title="Data Justice Assistent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@600;700&display=swap');

/* =========================================================
ROOT TOKENS
========================================================= */

:root{

    --bg:#08111F;
    --bg-soft:#0F1728;

    --panel:rgba(17,28,49,.72);
    --panel-strong:rgba(17,28,49,.92);

    --border:rgba(255,255,255,.06);

    --text:#F3F7FF;
    --muted:#8EA0BF;

    --blue:#4C8DFF;
    --green:#1DB87A;
    --amber:#F59E0B;
    --red:#EF4444;

    --radius:18px;
}

/* =========================================================
REMOVE STREAMLIT DEFAULTS
========================================================= */

#MainMenu,
footer,
header{
    visibility:hidden;
}

html,
body,
.stApp{
    font-family:'Inter',sans-serif !important;
    color:var(--text) !important;
}

/* =========================================================
APP BACKGROUND
========================================================= */

.stApp{

    background:
        radial-gradient(circle at top left,
            rgba(76,141,255,.10),
            transparent 28%),

        radial-gradient(circle at top right,
            rgba(76,141,255,.06),
            transparent 24%),

        linear-gradient(
            180deg,
            #08111F 0%,
            #0B1424 100%
        ) !important;

    min-height:100vh;
}

/* =========================================================
REMOVE DARK BLOCKS
========================================================= */

.main,
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
.element-container{
    background:transparent !important;
}

/* =========================================================
MAIN CONTENT WIDTH
========================================================= */

.main .block-container{

    max-width:1150px !important;

    padding-top:0 !important;
    padding-left:3rem !important;
    padding-right:3rem !important;
    padding-bottom:8rem !important;
}

/* =========================================================
SIDEBAR
========================================================= */

section[data-testid="stSidebar"]{

    background:
        linear-gradient(
            180deg,
            rgba(15,23,40,.96),
            rgba(10,17,31,.98)
        ) !important;

    border-right:1px solid rgba(255,255,255,.05);

    width:300px !important;
}

section[data-testid="stSidebar"] *{
    color:var(--text) !important;
}

section[data-testid="stSidebar"] p{
    color:var(--muted) !important;
}

section[data-testid="stSidebar"] button{

    background:rgba(255,255,255,.03) !important;

    border:1px solid rgba(255,255,255,.05) !important;

    border-radius:14px !important;

    color:var(--text) !important;

    transition:.18s ease;
}

section[data-testid="stSidebar"] button:hover{

    border:1px solid rgba(76,141,255,.35) !important;

    background:rgba(76,141,255,.08) !important;
}

/* =========================================================
TOPBAR
========================================================= */

.topbar{

    position:sticky;
    top:0;
    z-index:999;

    height:74px;

    display:flex;
    align-items:center;

    padding:0 28px;

    background:rgba(11,18,32,.72);

    backdrop-filter:blur(18px);

    border-bottom:1px solid rgba(255,255,255,.05);
}

.topbar-logo{

    display:flex;
    align-items:center;
    gap:12px;

    font-family:'Sora',sans-serif;

    font-size:15px;
    font-weight:700;
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

/* =========================================================
CHAT
========================================================= */

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

/* =========================================================
BUBBLES
========================================================= */

.bubble-bot{

    width:fit-content;
    max-width:72%;

    background:
        linear-gradient(
            180deg,
            rgba(23,35,56,.95),
            rgba(17,28,49,.95)
        );

    border:1px solid rgba(255,255,255,.05);

    border-radius:18px 18px 18px 6px;

    padding:18px 20px;

    line-height:1.7;
    font-size:13px;

    backdrop-filter:blur(16px);

    box-shadow:
        0 12px 40px rgba(0,0,0,.22);
}

.bubble-user{

    width:fit-content;
    max-width:66%;

    background:
        linear-gradient(
            180deg,
            #4C8DFF,
            #3777E8
        );

    border-radius:18px 18px 6px 18px;

    padding:18px 20px;

    line-height:1.7;
    font-size:13px;

    color:white;

    box-shadow:
        0 10px 28px rgba(76,141,255,.25);
}

/* =========================================================
CARDS
========================================================= */

.persona-card,
.metric-card,
.xai-box{

    background:rgba(17,28,49,.72);

    border:1px solid rgba(255,255,255,.05);

    border-radius:22px;

    backdrop-filter:blur(16px);

    box-shadow:
        0 20px 50px rgba(0,0,0,.22);
}

.persona-card{
    padding:24px;
    margin-top:18px;
}

.xai-box{
    margin-top:18px;
    padding:20px;
}

.metric-card{
    padding:20px;
    text-align:center;
}

/* =========================================================
RELIABILITY BAR
========================================================= */

.rel-bar{

    position:sticky;
    bottom:92px;

    z-index:99;

    width:fit-content;

    margin:0 auto 24px auto;

    display:flex;
    align-items:center;
    gap:10px;

    background:rgba(11,18,32,.78);

    border:1px solid rgba(255,255,255,.05);

    border-radius:999px;

    padding:12px 18px;

    backdrop-filter:blur(16px);

    box-shadow:
        0 10px 40px rgba(0,0,0,.35);
}

/* =========================================================
BADGES
========================================================= */

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

/* =========================================================
INPUT
========================================================= */

[data-testid="stForm"]{

    position:sticky;
    bottom:0;

    background:
        linear-gradient(
            180deg,
            rgba(8,17,31,0),
            rgba(8,17,31,.96) 35%
        );

    backdrop-filter:blur(18px);

    padding-top:20px;

    border:none !important;

    z-index:999;
}

.stTextInput input{

    height:56px !important;

    background:rgba(17,28,49,.95) !important;

    border:1px solid rgba(255,255,255,.06) !important;

    border-radius:16px !important;

    color:white !important;

    font-size:14px !important;

    padding:0 18px !important;
}

.stTextInput input:focus{

    border:1px solid rgba(76,141,255,.45) !important;

    box-shadow:
        0 0 0 4px rgba(76,141,255,.08) !important;
}

/* =========================================================
BUTTONS
========================================================= */

.stButton button{

    height:56px !important;

    border:none !important;

    border-radius:16px !important;

    background:
        linear-gradient(
            180deg,
            #4C8DFF,
            #3777E8
        ) !important;

    color:white !important;

    font-weight:600 !important;

    box-shadow:
        0 8px 24px rgba(76,141,255,.22);

    transition:.18s ease;
}

.stButton button:hover{

    transform:translateY(-1px);

    box-shadow:
        0 14px 34px rgba(76,141,255,.35);
}

/* =========================================================
TEXT
========================================================= */

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

.pc-tag{

    display:inline-flex;

    padding:5px 12px;

    border-radius:999px;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.06);

    color:#A8B7D3;

    font-size:11px;

    margin:5px 5px 0 0;
}

/* =========================================================
SPACING
========================================================= */

.element-container{
    margin-bottom:.45rem !important;
}

[data-testid="stVerticalBlock"]{
    gap:0rem !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TOPBAR
# =========================================================

st.markdown("""
<div class="topbar">

    <div class="topbar-logo">
        ⚖️ Data Justice Assistent
    </div>

    <div style="margin-left:14px">

        <div class="topbar-project">
            ReumaNederland Project
        </div>

        <div class="topbar-sub">
            Research Environment · Archive_4
        </div>

    </div>

</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## Personas")

    st.button("Alex Johnson", use_container_width=True)
    st.button("Thomas Kemp", use_container_width=True)
    st.button("Fatima Mansour", use_container_width=True)

    st.markdown("---")

    st.markdown("## Projects")

    st.button("ReumaNederland", use_container_width=True)
    st.button("Project 1", use_container_width=True)

# =========================================================
# CHAT EXAMPLE
# =========================================================

st.markdown("""

<div class="msg-wrap-bot">

    <div class="msg-time">
        14:32
    </div>

    <div class="msg-sender">
        🤖 Synthetic User · Alex Johnson
    </div>

    <div class="bubble-bot">
        Ik probeer actief te blijven ondanks mijn vermoeidheid.
        Vooral plannen blijft lastig omdat mijn energie per dag verschilt.
    </div>

</div>

<div class="msg-wrap-user">

    <div class="msg-time">
        14:33
    </div>

    <div class="bubble-user">
        Hoe ervaar je het gebruik van digitale zorgapps?
    </div>

</div>

""", unsafe_allow_html=True)

# =========================================================
# RELIABILITY BAR
# =========================================================

st.markdown("""

<div class="rel-bar">

    <span style="font-size:11px;color:#8EA0BF">
        Reliability
    </span>

    <span class="rel-badge-green">
        ✓ Bias laag
    </span>

    <span class="rel-badge-amber">
        ⚠ Hallucinaties medium
    </span>

    <span class="rel-badge-red">
        ✗ Inclusie risico
    </span>

</div>

""", unsafe_allow_html=True)

# =========================================================
# PERSONA CARD
# =========================================================

st.markdown("""

<div class="persona-card">

    <div style="display:flex;justify-content:space-between">

        <div>

            <div style="
                font-size:22px;
                font-weight:700;
                font-family:'Sora',sans-serif;
            ">
                Alex Johnson
            </div>

            <div style="
                color:#72A7FF;
                font-size:12px;
                margin-top:4px;
            ">
                Reumatoïde artritis · 52 jaar
            </div>

        </div>

        <div style="
            width:64px;
            height:64px;
            border-radius:18px;
            background:rgba(76,141,255,.12);
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:700;
            color:#72A7FF;
        ">
            AJ
        </div>

    </div>

    <div style="
        margin-top:18px;
        color:#8EA0BF;
        line-height:1.7;
        font-style:italic;
    ">
        “Ik wil mijn leven blijven leiden,
        maar de vermoeidheid maakt plannen moeilijk.”
    </div>

    <div style="margin-top:18px">

        <span class="pc-tag">Vermoeidheid</span>
        <span class="pc-tag">Zelfstandigheid</span>
        <span class="pc-tag">Pijnbeheer</span>

    </div>

</div>

""", unsafe_allow_html=True)

# =========================================================
# INPUT
# =========================================================

with st.form("chat_form", clear_on_submit=True):

    col1, col2 = st.columns([6,1])

    with col1:

        st.text_input(
            "Vraag",
            placeholder="Ask the Synthetic User...",
            label_visibility="collapsed"
        )

    with col2:

        st.form_submit_button("Send")
```
