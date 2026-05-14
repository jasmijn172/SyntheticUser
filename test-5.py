"""
Data Justice Assistent — Streamlit versie met eigen dataset
Upload cleaned_reuma_enquete_V03.csv (of vergelijkbaar) om persona's te genereren.
"""

import streamlit as st
import json
import re
import pandas as pd
import numpy as np
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Justice Assistent",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLING ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; background:#05080f; color:#f0f4f8; }
section[data-testid="stSidebar"] { background:#080e1a !important; border-right:1px solid #1a2d45; }
section[data-testid="stSidebar"] * { color:#b0c4dc; }
.main .block-container { background:#05080f; padding-top:1.2rem; max-width:100%; }

.user-msg   { background:#0F3460; border:1px solid #3b82f633; border-radius:12px 4px 12px 12px; padding:12px 16px; margin:8px 0 8px 60px; font-size:14px; color:#f0f4f8; line-height:1.6; }
.assistant-msg { background:#0b1422; border:1px solid #1a2d45; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 60px 8px 0; font-size:14px; color:#b0c4dc; line-height:1.6; }
.msg-meta   { font-size:11px; color:#3d5a78; margin-bottom:4px; }

.persona-card { background:#0b1422; border:1px solid #1a2d45; border-radius:12px; padding:16px; margin:8px 0 12px; }
.tag { display:inline-block; padding:2px 8px; border-radius:10px; background:#132238; color:#6b8aaa; font-size:11px; border:1px solid #1a2d45; margin:2px; }

.pill-green { background:#0d4a38; color:#1D9E75; border:1px solid #1D9E7544; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin:2px; }
.pill-amber { background:#422a08; color:#d97706; border:1px solid #d9770644; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin:2px; }
.pill-red   { background:#4a0e0e; color:#dc2626; border:1px solid #dc262644; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; display:inline-block; margin:2px; }

.xai-block  { background:#0f1c30; border:1px solid #1a2d45; border-radius:8px; padding:12px; margin-top:10px; }
.score-card { background:#0b1422; border:1px solid #1a2d45; border-radius:10px; padding:14px; }

.stButton button { background:#0f1c30 !important; border:1px solid #1a2d45 !important; color:#b0c4dc !important; border-radius:8px !important; font-size:12px !important; }
.stButton button:hover { background:#132238 !important; border-color:#243d5c !important; }
.stTextInput input, .stTextArea textarea { background:#0b1422 !important; border:1px solid #1a2d45 !important; color:#f0f4f8 !important; border-radius:10px !important; }
.stSelectbox > div > div { background:#0b1422 !important; border:1px solid #1a2d45 !important; color:#f0f4f8 !important; }
div[data-testid="stExpander"] { background:#0b1422; border:1px solid #1a2d45; border-radius:8px; }
.stTabs [data-baseweb="tab-list"] { background:#080e1a; border-bottom:1px solid #1a2d45; }
.stTabs [data-baseweb="tab"]      { color:#6b8aaa; font-size:12px; }
.stTabs [aria-selected="true"]    { color:#f0f4f8 !important; border-bottom-color:#3b82f6 !important; }
hr { border-color:#1a2d45 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def score_color(s):
    return "#1D9E75" if s>=81 else "#d97706" if s>=71 else "#dc2626"
def score_label(s):
    return "Low" if s>=81 else "Medium" if s>=71 else "High"
def score_icon(s):
    return "✓" if s>=81 else "⚠" if s>=71 else "✕"
def pill_class(s):
    return "pill-green" if s>=81 else "pill-amber" if s>=71 else "pill-red"
def pill_html(label, score):
    return f'<span class="{pill_class(score)}">{score_icon(score)} {label} – {score_label(score)}</span>'

def parse_scores(raw):
    try:
        m = re.search(r'<<<SCORES>>>([\s\S]*?)<<<END>>>', raw)
        if m: return json.loads(m.group(1).strip())
    except: pass
    try:
        m = re.search(r'\{[\s\S]*?"bias_score"[\s\S]*?\}', raw)
        if m: return json.loads(m.group(0))
    except: pass
    return None

def clean_text(raw):
    t = re.sub(r'<<<SCORES>>>[\s\S]*?<<<END>>>', '', raw)
    t = re.sub(r'\{[\s\S]*?"bias_score"[\s\S]*?\}', '', t)
    return t.strip()

# ─── DATASET CLEANING (zelfde logica als notebook V03) ────────────────────────
def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Past dezelfde cleaning toe als Reuma_Enquete_Cleaning_V03.ipynb"""
    df = df.copy()

    # Verwijder metadata kolommen als die aanwezig zijn
    for col in ['Start Date (UTC)', 'Response Type', '#']:
        if col in df.columns:
            df = df.drop(columns=[col])

    # Leeftijd naar numeriek
    age_col = next((c for c in df.columns if 'leeftijd' in c.lower()), None)
    if age_col:
        age_map = {'26 – 35':30.5,'36 – 45':40.5,'46 – 55':50.5,'56 – 65':60.5,'66 – 75':70.5,'> 75':80}
        df[age_col] = df[age_col].map(lambda x: age_map.get(str(x).strip(), pd.to_numeric(x, errors='coerce')))

    # Reumaduur naar numeriek
    dur_col = next((c for c in df.columns if 'lang' in c.lower() and 'reuma' in c.lower()), None)
    if dur_col:
        dur_map = {'Ik heb geen reuma':0,'Korter dan 1 jaar':0.5,'1 - 5 jaar':3,'5 - 10 jaar':7.5,'Langer dan 10 jaar':15}
        df[dur_col] = df[dur_col].map(lambda x: dur_map.get(str(x).strip(), pd.to_numeric(x, errors='coerce')))

    return df

# ─── DATASET ANALYSE → PERSONA GENERATIE ──────────────────────────────────────
def dataset_summary(df: pd.DataFrame) -> str:
    """Maak een compacte samenvatting van de dataset voor de LLM."""
    lines = [f"Dataset: {len(df)} respondenten, {len(df.columns)} kolommen\n"]

    # Kolommen tonen
    lines.append("Kolommen: " + ", ".join(df.columns.tolist()[:20]))

    # Numerieke statistieken
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        lines.append("\nNumerieke kolommen (gemiddelde / mediaan / min / max):")
        for col in num_cols[:8]:
            vals = df[col].dropna()
            if len(vals):
                lines.append(f"  {col}: gem={vals.mean():.1f} | med={vals.median():.1f} | {vals.min():.0f}–{vals.max():.0f}")

    # Categorische waarden (top 5 per kolom)
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        lines.append("\nCategorische kolommen (top waarden):")
        for col in cat_cols[:10]:
            vc = df[col].value_counts().head(4)
            if len(vc):
                top = " | ".join([f"{v}({c})" for v, c in vc.items()])
                lines.append(f"  {col}: {top}")

    return "\n".join(lines)

def generate_personas_from_data(df: pd.DataFrame, n_personas: int = 4) -> list[dict]:
    """Gebruik Claude om persona's te genereren op basis van de dataset."""
    summary = dataset_summary(df)

    prompt = f"""Je bent een Data Justice onderzoeker. Analyseer deze enquêtedata van ReumaNederland en genereer {n_personas} realistische, diverse synthetic user persona's.

DATASET SAMENVATTING:
{summary}

EERSTE 5 RIJEN (steekproef):
{df.head(5).to_string()}

Genereer {n_personas} persona's die de diversiteit in de dataset weerspiegelen (leeftijd, reumaduur, digitale vaardigheid, behoeften). Let op inclusie en vermijd stereotypen.

Geef ALLEEN geldig JSON terug, geen uitleg erbuiten:
{{
  "personas": [
    {{
      "naam": "...",
      "age": <getal>,
      "initials": "<2 letters>",
      "geslacht": "...",
      "diagnose": "...",
      "context": "...",
      "doelen": "...",
      "frustraties": "...",
      "tech": "Laag|Gemiddeld|Hoog|Expert",
      "quote": "...",
      "tags": ["...", "...", "..."],
      "kenmerken": ["...", "...", "..."],
      "factoren": ["...", "...", "..."],
      "uitleg": "...",
      "data_basis": "Gebaseerd op [X] respondenten met vergelijkbaar profiel in de dataset."
    }}
  ]
}}"""

    if "groq_api_key" not in st.session_state or not st.session_state.groq_api_key:
        raise ValueError("Groq API key ontbreekt. Vul deze in de zijbalk in.")
        
    client = Groq(api_key=st.session_state.groq_api_key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.choices[0].message.content
    # JSON extraheren
    m = re.search(r'\{[\s\S]*\}', raw)
    if m:
        data = json.loads(m.group(0))
        return data.get("personas", [])
    return []

# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────
def build_prompt(p: dict, mood: str, dataset_context: str = "") -> str:
    dc = f"\nRELEVANTE DATA UIT DE DATASET:\n{dataset_context}\n" if dataset_context else ""
    return f"""Je bent een Synthetic User — een cognitieve agent die volledig in-character reageert als de persona hieronder. Je bent GEEN assistent; je bent {p['naam']}.

PERSONA: {p['naam']}, {p['age']}jr, {p['geslacht']}
Diagnose: {p['diagnose']} | Context: {p['context']}
Doelen: {p['doelen']} | Frustraties: {p['frustraties']}
Tech-vaardigheid: {p['tech']} | Huidige stemming: {mood}
Quote: "{p['quote']}"
{dc}
GEDRAGSREGELS:
- Reageer altijd in de eerste persoon als {p['naam']}
- Laat stemming "{mood}" doorklinken in toon en woordkeuze
- Baseer je antwoorden op echte ervaringen die passen bij de dataset
- Antwoord in het Nederlands (of Engels als de vraag in het Engels is)
- Reageer als een echte persoon, geen lijstjes

BIAS-JUSTICE VALIDATIE (notebook JasmijnPelle_bias_justice_personas):
Voeg na elk antwoord dit blok toe:
<<<SCORES>>>
{{"bias_score": <0-100>, "hallucination_score": <0-100>, "inclusie_score": <0-100>, "bias_toelichting": "<1 zin>", "hallucinatie_toelichting": "<1 zin>", "inclusie_toelichting": "<1 zin>"}}
<<<END>>>

Scoreschaal: 81-100=groen(goed) | 71-80=geel(aandacht) | 0-70=rood(problematisch). Hogere score = beter."""

# ─── SESSION STATE ────────────────────────────────────────────────────────────
defaults = {
    "messages": [], "scores_hist": [], "latest_scores": None,
    "personas": [], "active_persona_idx": 0,
    "mood": "Curious", "df": None, "dataset_name": "",
    "generating": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

MOODS = ["Curious", "Confused", "Distrust", "Frustrated", "Hopeful", "Overstimulated"]

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚖ Data Justice Assistent")
    st.markdown("---")
    
    st.markdown("**🔑 API Instellingen**")
    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", value=st.session_state.get("groq_api_key", ""))
    if api_key:
        st.session_state.groq_api_key = api_key
    st.markdown("---")

    # ── Dataset upload ──
    st.markdown("**📂 Jouw dataset**")
    uploaded = st.file_uploader(
        "Upload cleaned_reuma_enquete_V03.csv",
        type=["csv", "xlsx"],
        label_visibility="collapsed",
        help="Upload het gecleande CSV-bestand uit jouw notebook",
    )

    if uploaded:
        try:
            if uploaded.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded)
            else:
                df = pd.read_csv(uploaded, low_memory=False)

            df = clean_dataset(df)
            st.session_state.df           = df
            st.session_state.dataset_name = uploaded.name

            st.success(f"✓ {len(df)} rijen · {len(df.columns)} kolommen geladen")

            with st.expander("Kolommen preview"):
                st.dataframe(df.head(3), use_container_width=True)

        except Exception as e:
            st.error(f"Fout bij laden: {e}")

    if st.session_state.df is not None:
        n = st.slider("Aantal persona's genereren", 2, 6, 4)
        if st.button("🔄 Genereer persona's uit dataset", use_container_width=True):
            with st.spinner("Claude analyseert jouw data en genereert persona's…"):
                try:
                    personas = generate_personas_from_data(st.session_state.df, n_personas=n)
                    if personas:
                        st.session_state.personas         = personas
                        st.session_state.active_persona_idx = 0
                        st.session_state.messages         = []
                        st.session_state.scores_hist      = []
                        st.session_state.latest_scores    = None
                        st.success(f"✓ {len(personas)} persona's gegenereerd!")
                        st.rerun()
                    else:
                        st.error("Geen persona's gegenereerd. Controleer de API-key.")
                except Exception as e:
                    st.error(f"Fout: {e}")

    st.markdown("---")

    # ── Persona selectie ──
    if st.session_state.personas:
        st.markdown("**Persona's**")
        st.markdown('<div style="font-size:11px;color:#3b82f6;margin-bottom:6px;">Gegenereerd uit jouw dataset</div>', unsafe_allow_html=True)

        for i, p in enumerate(st.session_state.personas):
            is_active = i == st.session_state.active_persona_idx
            bg     = "#0f1c30" if is_active else "transparent"
            border = "#3b82f655" if is_active else "#1a2d45"
            if st.button(
                f"{'▶ ' if is_active else ''}{p['naam']} · {p['age']}jr",
                key=f"p_{i}",
                use_container_width=True,
            ):
                if i != st.session_state.active_persona_idx:
                    st.session_state.active_persona_idx = i
                    st.session_state.messages           = []
                    st.session_state.scores_hist        = []
                    st.session_state.latest_scores      = None
                    st.rerun()
    else:
        st.markdown('<div style="color:#3d5a78;font-size:12px;padding:8px 0;">⬆ Upload een dataset en genereer persona\'s</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.session_state.mood = st.selectbox("🎭 Mood checker", MOODS, index=MOODS.index(st.session_state.mood))

    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:28px;height:28px;border-radius:50%;background:#3b82f6;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff;">DS</div>
        <div><div style="font-size:12px;color:#f0f4f8;">Designer</div><div style="font-size:11px;color:#6b8aaa;">Greenberry</div></div>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

# Top bar
col_t, col_m, col_e = st.columns([4, 1.5, 1])
with col_t:
    ds_name = st.session_state.dataset_name or "Geen dataset geladen"
    st.markdown(f"""
    <div>
        <div style="font-size:18px;font-weight:700;color:#3b82f6;">ReumaNederland Project</div>
        <div style="font-size:11px;color:#6b8aaa;">🗄 {ds_name} · Team 3</div>
    </div>
    """, unsafe_allow_html=True)
with col_m:
    st.markdown(f'<div style="padding-top:8px;font-size:12px;color:#6b8aaa;">Stemming: <span style="color:#b0c4dc;">{st.session_state.mood}</span></div>', unsafe_allow_html=True)
with col_e:
    st.button("↑ Export", use_container_width=True)

st.markdown("---")

# ── Geen persona's: welkomstscherm ──
if not st.session_state.personas:
    st.markdown("""
    <div style="padding: 40px 20px; min-height: 70vh;">
        <h1 style="font-size: 3.8rem; color: #7B9AF5; font-family: 'Times New Roman', serif; margin-bottom: 10px; line-height: 1.1;">
            Synthetic User and<br>Data Justice Assistent
        </h1>
        <p style="color: #6b8aaa; font-size: 1.1rem; max-width: 600px; margin-bottom: 50px;">
            Genereer synthetische respondenten op basis van jouw data. Track live bias, hallucinatie en data justice scores.
        </p>
        
        <div style="margin-top: 50px; max-width: 800px;">
            <p style="color: #b0c4dc; font-size: 0.85rem; margin-bottom: 8px;">Ask the Synthetic User</p>
            <div style="display: flex; gap: 15px; align-items: center;">
                <span style="font-size: 32px; color: #5B7AFA; font-weight: bold;">+</span>
                <div style="flex: 1; background: #ffffff; padding: 12px 20px; border-radius: 8px; color: #999;">
                    Upload een dataset in de zijbalk en genereer persona's...
                </div>
                <button disabled style="background: #5B7AFA; color: white; border: none; padding: 14px 30px; border-radius: 8px; font-weight: bold; cursor: not-allowed; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 16px;">✈</span> Send
                </button>
            </div>
        </div>
        
        <div style="display: flex; gap: 20px; margin-top: 100px; padding: 25px; background: rgba(11, 20, 34, 0.7); border: 1px solid #1a2d45; border-radius: 12px; max-width: 900px; backdrop-filter: blur(10px);">
            <div style="display: flex; gap: 15px; align-items: center; flex: 1;">
                <div style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #5B7AFA; display: flex; align-items: center; justify-content: center; color: #5B7AFA; font-size: 18px;">
                    👤
                </div>
                <div>
                    <div style="font-size: 0.95rem; color: #f0f4f8; font-weight: 600;">Diverse Perspectives</div>
                    <div style="font-size: 0.8rem; color: #6b8aaa; margin-top: 2px;">Engage synthetic users to explore multiple viewpoints</div>
                </div>
            </div>
            <div style="width: 1px; background: #1a2d45; margin: 0 10px;"></div>
            <div style="display: flex; gap: 15px; align-items: center; flex: 1;">
                <div style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #1D9E75; display: flex; align-items: center; justify-content: center; color: #1D9E75; font-size: 18px;">
                    🛡
                </div>
                <div>
                    <div style="font-size: 0.95rem; color: #f0f4f8; font-weight: 600;">Transparent Insights</div>
                    <div style="font-size: 0.8rem; color: #6b8aaa; margin-top: 2px;">Real-time reliability indicators help you evaluate with confidence</div>
                </div>
            </div>
            <div style="width: 1px; background: #1a2d45; margin: 0 10px;"></div>
            <div style="display: flex; gap: 15px; align-items: center; flex: 1;">
                <div style="width: 44px; height: 44px; border-radius: 50%; border: 2px solid #5B7AFA; display: flex; align-items: center; justify-content: center; color: #5B7AFA; font-size: 18px;">
                    🔍
                </div>
                <div>
                    <div style="font-size: 0.95rem; color: #f0f4f8; font-weight: 600;">Organized Research</div>
                    <div style="font-size: 0.8rem; color: #6b8aaa; margin-top: 2px;">Keep projects structured and findings export ready</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Actieve persona ──
p = st.session_state.personas[st.session_state.active_persona_idx]

# ── Persona kaart ──
with st.expander(f"👤 {p['naam']} — {p['diagnose']}", expanded=len(st.session_state.messages) == 0):
    col_av, col_info, col_grid = st.columns([1, 2.5, 2.5])
    with col_av:
        st.markdown(f"""
        <div style="width:70px;height:70px;border-radius:10px;background:linear-gradient(135deg,#1a3a5c,#0d4a38);
             display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:#5DCAA5;">
             {p.get('initials','??')}
        </div>""", unsafe_allow_html=True)
    with col_info:
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in p.get('tags', []))
        st.markdown(f"""
        <div style="font-size:16px;font-weight:700;color:#f0f4f8;">{p['naam']}
            <span style="font-size:12px;background:#132238;color:#6b8aaa;padding:2px 8px;border-radius:12px;border:1px solid #1a2d45;">{p['age']} yrs</span>
        </div>
        <div style="font-size:12px;color:#1D9E75;margin-bottom:6px;">{p['geslacht']} · <span style="color:#e57373;">{p['diagnose']}</span></div>
        <div style="font-size:12px;color:#6b8aaa;font-style:italic;margin-bottom:8px;">"{p.get('quote','')}"</div>
        {tags_html}
        """, unsafe_allow_html=True)
    with col_grid:
        for icon, label, key in [("📋","Context","context"),("🎯","Doelen","doelen"),("⚡","Frustraties","frustraties"),("💻","Tech",  "tech")]:
            st.markdown(f"""
            <div style="display:flex;gap:8px;margin-bottom:5px;">
                <span style="color:#6b8aaa;font-size:12px;min-width:100px;">{icon} {label}</span>
                <span style="font-size:12px;color:#b0c4dc;">{p.get(key,'')}</span>
            </div>""", unsafe_allow_html=True)

    # Data basis badge
    if p.get("data_basis"):
        st.markdown(f'<div style="font-size:11px;color:#3b82f6;margin-top:8px;">📊 {p["data_basis"]}</div>', unsafe_allow_html=True)

    # Explainable AI
    factoren_html = "".join(f'<span class="tag">{f}</span>' for f in p.get('factoren', []))
    st.markdown(f"""
    <div class="xai-block">
        <div style="font-size:12px;font-weight:600;color:#b0c4dc;margin-bottom:8px;">
            ▼ Why was this created this way? <span style="color:#3b82f6;">Explainable AI</span> ⓘ
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
            <div>
                <div style="font-size:11px;color:#6b8aaa;margin-bottom:4px;font-weight:600;">Data bron</div>
                <div style="font-size:11px;color:#b0c4dc;">• {st.session_state.dataset_name}<br>• {len(st.session_state.df)} respondenten</div>
            </div>
            <div>
                <div style="font-size:11px;color:#6b8aaa;margin-bottom:6px;font-weight:600;">Key factors</div>
                {factoren_html}
            </div>
            <div>
                <div style="font-size:11px;color:#6b8aaa;margin-bottom:4px;font-weight:600;">Explanation</div>
                <div style="font-size:11px;color:#b0c4dc;line-height:1.5;">{p.get('uitleg','')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Dataset context voor chat ──
def get_dataset_context(df: pd.DataFrame, p: dict) -> str:
    """Haal relevante rijen op die passen bij de persona."""
    if df is None or df.empty:
        return ""
    age_col = next((c for c in df.columns if 'leeftijd' in c.lower()), None)
    sample = df
    if age_col:
        try:
            sample = df[(df[age_col] >= p['age'] - 15) & (df[age_col] <= p['age'] + 15)].head(5)
            if sample.empty:
                sample = df.head(5)
        except:
            sample = df.head(5)
    else:
        sample = df.head(5)
    return f"Vergelijkbare respondenten uit de dataset (steekproef {len(sample)} rijen):\n{sample.to_string()}"

# ── Chat ──
time_str = datetime.now().strftime("%H:%M")
st.markdown(f"""
<div class="msg-meta">{time_str}</div>
<div class="assistant-msg">⚖ Hi! Ik ben {p['naam']}. Stel me gerust een vraag over mijn ervaringen met {p['diagnose']}.</div>
""", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="text-align:right;">
            <div class="msg-meta" style="text-align:right;">{time_str} DS</div>
            <div class="user-msg">{msg['content']}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-meta">{time_str} <b>Synthetic User</b> · Gebaseerd op {st.session_state.dataset_name}</div>
        <div class="assistant-msg">⚖ {msg['content']}</div>
        """, unsafe_allow_html=True)
        if msg.get("scores"):
            sc = msg["scores"]
            st.markdown(
                pill_html("Bias", sc["bias_score"]) + " " +
                pill_html("Hallucinatie", sc["hallucination_score"]) + " " +
                pill_html("Data Justice", sc["inclusie_score"]),
                unsafe_allow_html=True,
            )

st.markdown("---")

# ── Live dashboard ──
if st.session_state.latest_scores:
    sc = st.session_state.latest_scores
    st.markdown("### 📊 Live Reliability Dashboard")
    cols = st.columns(3)
    for col, label, score, tip in [
        (cols[0], "Hallucinatie", sc["hallucination_score"], sc.get("hallucinatie_toelichting","")),
        (cols[1], "Bias",         sc["bias_score"],          sc.get("bias_toelichting","")),
        (cols[2], "Data Justice", sc["inclusie_score"],      sc.get("inclusie_toelichting","")),
    ]:
        color = score_color(score)
        with col:
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:12px;color:#6b8aaa;">{label}</div>
                <div style="font-size:28px;font-weight:700;color:{color};">{score}%</div>
                <div style="font-size:11px;color:#6b8aaa;">{score_icon(score)} {score_label(score)}</div>
                <div style="width:100%;height:6px;background:#132238;border-radius:3px;margin:8px 0;overflow:hidden;">
                    <div style="width:{score}%;height:100%;background:{color};border-radius:3px;"></div>
                </div>
                <div style="font-size:11px;color:#6b8aaa;line-height:1.4;">{tip}</div>
            </div>""", unsafe_allow_html=True)

    total = round((sc["bias_score"] + sc["hallucination_score"] + sc["inclusie_score"]) / 3)
    tc = score_color(total)
    st.markdown(f"""
    <div style="background:#0b1422;border:1px solid #1a2d45;border-radius:10px;padding:14px;margin-top:10px;display:flex;align-items:center;gap:20px;">
        <div><div style="font-size:12px;color:#6b8aaa;">Totaalscore</div>
             <div style="font-size:30px;font-weight:700;color:{tc};">{total}%</div>
             <div style="font-size:12px;color:{tc};">{score_icon(total)} {score_label(total)}</div></div>
        <div style="flex:1;">
            <div style="width:100%;height:10px;background:#132238;border-radius:5px;overflow:hidden;">
                <div style="width:{total}%;height:100%;background:{tc};border-radius:5px;"></div>
            </div>
            <div style="font-size:11px;color:#6b8aaa;margin-top:6px;">🔴 0-70 problematisch · 🟡 71-80 aandacht · 🟢 81-100 goed</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if len(st.session_state.scores_hist) > 1:
        st.markdown("**Score-verloop**")
        df_h = pd.DataFrame(st.session_state.scores_hist, columns=["Bias","Hallucinatie","Inclusie"])
        st.line_chart(df_h, height=140)

    with st.expander("💡 Verbeteringsuggesties"):
        for tip in [
            "Voeg meer context toe voor betere representatie van de persona",
            "Verfijn de prompt voor specifieker gedrag",
            "Controleer de dataset op ondervertegenwoordigde groepen",
        ]:
            st.markdown(f"✦ {tip}")

    st.markdown("---")

# ── Input ──
st.markdown(f"**Ask the Synthetic User ✦** _{p['naam']} · {st.session_state.mood}_")
with st.form("chat_form", clear_on_submit=True):
    col_i, col_b = st.columns([5, 1])
    with col_i:
        user_input = st.text_input("Vraag", placeholder=f"Stel een vraag aan {p['naam']}...", label_visibility="collapsed")
    with col_b:
        submitted = st.form_submit_button("✈ Send", use_container_width=True)

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner(f"⚖ {p['naam']} denkt na…"):
        try:
            dc       = get_dataset_context(st.session_state.df, p)
            if "groq_api_key" not in st.session_state or not st.session_state.groq_api_key:
                st.error("Vul eerst je Groq API key in (sidebar).")
                st.stop()
            client_chat = Groq(api_key=st.session_state.groq_api_key)
            api_msgs = [{"role": "system", "content": build_prompt(p, st.session_state.mood, dc)}] + \
                       [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            resp     = client_chat.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1000,
                messages=api_msgs,
            )
            raw  = resp.choices[0].message.content
            sc2  = parse_scores(raw)
            body = clean_text(raw)
            if sc2:
                st.session_state.latest_scores = sc2
                st.session_state.scores_hist.append([sc2["bias_score"], sc2["hallucination_score"], sc2["inclusie_score"]])
            st.session_state.messages.append({"role":"assistant","content":body,"scores":sc2})
        except Exception as e:
            st.error(f"API fout: {e}")
    st.rerun()

# ── Export ──
if st.session_state.messages:
    st.markdown("---")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        export = {
            "persona": p["naam"], "dataset": st.session_state.dataset_name,
            "mood": st.session_state.mood, "exported": datetime.now().isoformat(),
            "messages": st.session_state.messages,
            "laatste_scores": st.session_state.latest_scores,
            "score_history": st.session_state.scores_hist,
        }
        st.download_button(
            "📥 Export gesprek (JSON)",
            data=json.dumps(export, indent=2, ensure_ascii=False),
            file_name=f"data_justice_{p['naam'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json", use_container_width=True,
        )
    with col_ex2:
        if st.button("🔄 Nieuw gesprek", use_container_width=True):
            st.session_state.messages = []
            st.session_state.scores_hist = []
            st.session_state.latest_scores = None
            st.rerun()
