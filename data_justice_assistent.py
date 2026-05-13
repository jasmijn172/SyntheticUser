"""
Data Justice Assistent — Streamlit App
Synthetic User als cognitieve agent met real-time bias/hallucinatie/inclusie tracking
Gebouwd met Groq API (llama-3.3-70b-versatile) + LangGraph-geïnspireerde validatieflow
"""

import streamlit as st
import json
import os
import time
from groq import Groq

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

/* ── Globaal ── */
html, body, .stApp {
    background-color: #0B1220 !important;
    color: #F1F5F9 !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #253047 !important;
    min-width: 270px !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stRadio label span {
    color: #8B9CB8 !important;
    font-size: 13px !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
    font-family: 'Sora', sans-serif !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: #1a2438 !important;
    color: #8B9CB8 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    padding: 6px 12px !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1f2d47 !important;
    color: #F1F5F9 !important;
    border-color: #3B7EF6 !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1a2438 !important;
    border: 1px solid #253047 !important;
    color: #F1F5F9 !important;
    border-radius: 8px !important;
}

/* ── Topbar ── */
.topbar {
    background: #111827;
    border-bottom: 1px solid #253047;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.topbar-logo {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 15px;
    color: #F1F5F9;
    display: flex;
    align-items: center;
    gap: 8px;
}
.topbar-project {
    font-family: 'Sora', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #3B7EF6;
    margin-left: 12px;
}
.topbar-sub {
    font-size: 11px;
    color: #8B9CB8;
}

/* ── Chat berichten ── */
.msg-wrap-bot { display: flex; flex-direction: column; margin-bottom: 18px; }
.msg-wrap-user { display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 18px; }
.msg-time { font-size: 10px; color: #8B9CB8; margin-bottom: 4px; }
.msg-sender {
    font-size: 11px; color: #5B9BFF; font-weight: 600;
    margin-bottom: 5px; display: flex; align-items: center; gap: 6px;
}
.bubble-bot {
    background: #151f33;
    border: 1px solid #253047;
    border-radius: 12px 12px 12px 4px;
    padding: 12px 16px;
    max-width: 82%;
    font-size: 13px;
    line-height: 1.65;
    color: #F1F5F9;
}
.bubble-user {
    background: #3B7EF6;
    border-radius: 12px 12px 4px 12px;
    padding: 12px 16px;
    max-width: 72%;
    font-size: 13px;
    line-height: 1.65;
    color: white;
}

/* ── Persona kaart ── */
.persona-card {
    background: #1a2438;
    border: 1px solid #2E3D5A;
    border-radius: 14px;
    padding: 18px;
    margin-top: 10px;
    max-width: 800px;
}
.pc-name { font-family: 'Sora', sans-serif; font-size: 18px; font-weight: 700; color: #F1F5F9; margin-bottom: 2px; }
.pc-diag { font-size: 11px; color: #1DB87A; margin-bottom: 6px; }
.pc-quote { font-size: 12px; color: #8B9CB8; font-style: italic; line-height: 1.55; margin-bottom: 10px; }
.pc-age { background: rgba(59,126,246,.18); color: #5B9BFF; border-radius: 20px; padding: 3px 14px; font-size: 11px; font-weight: 700; display: inline-block; }
.pc-tag { display: inline-block; background: #111827; border: 1px solid #2E3D5A; color: #8B9CB8; border-radius: 20px; padding: 2px 10px; font-size: 10px; margin: 2px 2px 2px 0; }
.pc-det-label { color: #8B9CB8; font-size: 11px; min-width: 100px; }
.pc-det-val { color: #F1F5F9; font-size: 11px; }

/* ── XAI sectie ── */
.xai-box {
    background: #111827;
    border: 1px solid #253047;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 10px;
    max-width: 800px;
}
.xai-title { font-size: 13px; font-weight: 600; color: #F1F5F9; margin-bottom: 10px; }
.xai-accent { color: #5B9BFF; }
.xai-badge {
    display: inline-block;
    background: rgba(59,126,246,.15);
    color: #5B9BFF;
    border-radius: 12px;
    padding: 2px 9px;
    font-size: 10px;
    margin: 2px 2px 2px 0;
}
.xai-source { font-size: 11px; color: #F1F5F9; padding: 2px 0; }
.xai-source::before { content: "• "; color: #3B7EF6; }
.xai-expl { font-size: 11px; color: #8B9CB8; line-height: 1.5; }

/* ── Reliability badges ── */
.rel-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 24px;
    background: #111827;
    border-top: 1px solid #253047;
    flex-wrap: wrap;
}
.rel-label { font-size: 11px; color: #8B9CB8; }
.rel-badge-amber {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(245,158,11,.13); color: #F59E0B;
    border: 1px solid rgba(245,158,11,.3);
    border-radius: 20px; padding: 5px 14px; font-size: 11px; font-weight: 600;
}
.rel-badge-green {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(29,184,122,.1); color: #1DB87A;
    border: 1px solid rgba(29,184,122,.3);
    border-radius: 20px; padding: 5px 14px; font-size: 11px; font-weight: 600;
}
.rel-badge-blue {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(59,126,246,.1); color: #5B9BFF;
    border: 1px solid rgba(59,126,246,.25);
    border-radius: 20px; padding: 5px 14px; font-size: 11px; font-weight: 600;
}
.rel-badge-red {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(239,68,68,.12); color: #EF4444;
    border: 1px solid rgba(239,68,68,.3);
    border-radius: 20px; padding: 5px 14px; font-size: 11px; font-weight: 600;
}

/* ── Score ring ── */
.score-ring-outer { display: flex; flex-direction: column; align-items: center; padding: 16px 0; }

/* ── Sidebar persona items ── */
.persona-sidebar-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: 8px;
    border: 1px solid transparent;
    margin-bottom: 5px; cursor: pointer;
    transition: .15s;
}
.persona-sidebar-item.active { background: rgba(59,126,246,.12); border-color: rgba(59,126,246,.4); }

/* ── Input ── */
.stTextInput input {
    background: #1a2438 !important;
    border: 1px solid #2E3D5A !important;
    border-radius: 10px !important;
    color: #F1F5F9 !important;
    font-size: 13px !important;
    padding: 10px 16px !important;
}
.stTextInput input:focus { border-color: #3B7EF6 !important; }
.stTextInput input::placeholder { color: #8B9CB8 !important; }

/* ── Stuur-knop ── */
div[data-testid="stButton"] > button {
    background: #3B7EF6 !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    transition: .15s !important;
}
div[data-testid="stButton"] > button:hover {
    background: #5B9BFF !important;
}

/* ── Metric kaartjes ── */
.metric-card {
    background: #151f33;
    border: 1px solid #253047;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-val { font-size: 22px; font-weight: 700; margin-bottom: 2px; }
.metric-lbl { font-size: 10px; color: #8B9CB8; text-transform: uppercase; letter-spacing: .5px; }

/* ── Expander styling ── */
.streamlit-expanderHeader {
    background: #1a2438 !important;
    border: 1px solid #253047 !important;
    border-radius: 8px !important;
    color: #F1F5F9 !important;
    font-size: 13px !important;
}
.streamlit-expanderContent {
    background: #111827 !important;
    border: 1px solid #253047 !important;
    border-top: none !important;
}

/* ── Divider ── */
hr { border-color: #253047 !important; }

/* ── Selectbox ── */
.stSelectbox label { color: #8B9CB8 !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# GROQ CLIENT INIT
# ─────────────────────────────────────────────
def get_groq_client():
    """Haal Groq client op via st.secrets of omgevingsvariabele."""
    api_key = None
    # 1) Streamlit secrets (voorkeur bij deployment)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    # 2) Omgevingsvariabele als fallback
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)
    return None


# ─────────────────────────────────────────────
# PERSONA DATA (gebaseerd op notebook + ontwerp)
# ─────────────────────────────────────────────
PERSONAS = [
    {
        "id": 1,
        "initials": "AJ",
        "naam": "Alex Johnson",
        "leeftijd": 52,
        "geslacht": "Vrouw",
        "diagnose": "Reumatoïde artritis",
        "quote": "Ik wil mijn leven blijven leiden, maar de vermoeidheid maakt het moeilijk om te plannen of consistent te zijn.",
        "tags": ["Vermoeidheid", "Pijnbeheer", "Zelfstandigheid", "Work-life balance"],
        "context": "Werkt parttime en woont samen met partner",
        "goals": "Actief blijven, onafhankelijkheid behouden",
        "frustrations": "Onvoorspelbare vermoeidheid, beperkte energie",
        "tech_support": "Gemiddeld",
        "data_bronnen": ["ReumaNederland Interviews n=65", "Patiëntforum data", "Wetenschappelijke literatuur"],
        "sleutelfactoren": ["Diagnose", "Leefstijl", "Emotionele impact"],
        "xai_uitleg": "Gegenereerd op basis van patronen in de dataset. Vermoeidheid wordt vaak als uitdaging genoemd door vrouwen van 50+.",
        "kwaliteit": "goed",  # voor validatie
    },
    {
        "id": 2,
        "initials": "TK",
        "naam": "Thomas Kemp",
        "leeftijd": 34,
        "geslacht": "Man",
        "diagnose": "Artritis psoriatica",
        "quote": "Apps moeten gewoon werken. Ik heb geen tijd voor uitleg — geef me de info in 30 seconden.",
        "tags": ["Efficiëntie", "Werk", "Digitaal vaardig", "Tijdgebrek"],
        "context": "Fulltime werkend, druk gezinsleven met 2 kinderen",
        "goals": "Snel toegang tot informatie, alles mobiel",
        "frustrations": "Trage systemen, onnodige clicks, onduidelijke navigatie",
        "tech_support": "Hoog",
        "data_bronnen": ["ReumaNederland survey 2024", "Gebruikersinterviews n=12"],
        "sleutelfactoren": ["Leefstijl", "Werkdruk"],
        "xai_uitleg": "Technologisch vaardig profiel. Tijdschaarste is de dominante factor in dit persona.",
        "kwaliteit": "goed",
    },
    {
        "id": 3,
        "initials": "FM",
        "naam": "Fatima Mansour",
        "leeftijd": 68,
        "geslacht": "Vrouw",
        "diagnose": "Artrose & fibromyalgie",
        "quote": "Soms begrijp ik niet wat ze van me verwachten. Mijn dochter helpt me, maar ik wil dat zelf kunnen doen.",
        "tags": ["Lage digitale geletterdheid", "Afhankelijkheid", "Taalbarrière", "Inclusie"],
        "context": "Woont alleen, heeft informele zorger (dochter), spreekt Nederlands en Arabisch",
        "goals": "Begrijpen wat er van haar verwacht wordt, meer zelfredzaamheid",
        "frustrations": "Kleine tekst, onduidelijke iconen, medisch jargon",
        "tech_support": "Laag",
        "data_bronnen": ["ReumaNederland Interviews n=65", "Zorginstellingsdata", "Migranten gezondheidsonderzoek"],
        "sleutelfactoren": ["Inclusie", "Taalvaardigheid", "Toegankelijkheid"],
        "xai_uitleg": "Vertegenwoordigt een kwetsbare doelgroep. Laagdrempeligheid en toegankelijkheid zijn cruciaal.",
        "kwaliteit": "goed",
    },
    {
        "id": 4,
        "initials": "PK",
        "naam": "Pieter de Kruijk",
        "leeftijd": 47,
        "geslacht": "Man",
        "diagnose": "Reumatoïde artritis (8 jaar)",
        "quote": "Ik ben al 8 jaar patiënt. Ik weet meer over dit systeem dan sommige artsen.",
        "tags": ["Ervaringsdeskundige", "Hoge betrokkenheid", "Systeem-kritisch", "Beleidsinteresse"],
        "context": "Actief in patiëntenvereniging, schrijft ervaringsreviews online",
        "goals": "Transparantie over behandelingen, invloed op zorgbeleid",
        "frustrations": "Niet serieus genomen worden, gebrek aan co-creatie met patiënten",
        "tech_support": "Hoog",
        "data_bronnen": ["ReumaNederland community data", "Patiëntenpanel interviews"],
        "sleutelfactoren": ["Ervaringsjaren", "Betrokkenheid", "Systemisch begrip"],
        "xai_uitleg": "Expert-gebruikersprofiel met sterke mening over systeemintegriteit en transparantie.",
        "kwaliteit": "goed",
    },
    {
        "id": 5,
        "initials": "??",
        "naam": "Tech-savvy Millennial",
        "leeftijd": 30,
        "geslacht": "Onbekend",
        "diagnose": "Niet gespecificeerd",
        "quote": "Millennials gebruiken 73% vaker apps. Ze verwachten instant feedback.",
        "tags": ["Vaag", "Stereotyp", "Hallucinatief", "Onvolledig"],
        "context": "Niet gespecificeerd — te generiek profiel",
        "goals": "Onbekend",
        "frustrations": "Onbekend",
        "tech_support": "Onbekend",
        "data_bronnen": ["Onbekende bron (niet geverifieerd)", "Statistiek zonder referentie"],
        "sleutelfactoren": ["Leeftijdsstereotyp"],
        "xai_uitleg": "⚠️ Dit persona bevat mogelijk hallucinaties (73%-statistiek) en bias (leeftijdsstereotypering). Validatie aanbevolen.",
        "kwaliteit": "slecht",  # triggers hogere foutscores
    },
]


# ─────────────────────────────────────────────
# SCORE HULPFUNCTIES
# ─────────────────────────────────────────────
def score_kleur(score: int) -> str:
    if score >= 80:
        return "#1DB87A"  # groen
    elif score >= 60:
        return "#F59E0B"  # amber
    return "#EF4444"  # rood


def score_label(score: int) -> str:
    if score >= 80:
        return "Laag risico"
    elif score >= 60:
        return "Gemiddeld"
    return "Hoog risico"


def badge_html(score: int, label: str, icon: str) -> str:
    if score >= 80:
        cls = "rel-badge-green"
        prefix = "✓"
    elif score >= 60:
        cls = "rel-badge-amber"
        prefix = "⚠"
    else:
        cls = "rel-badge-red"
        prefix = "✗"
    return f'<span class="{cls}">{prefix} {label} — {score_label(score)}</span>'


def teken_score_ring(score: int, label: str = "Totaalscore"):
    """SVG score-ring zoals in het ontwerp."""
    kleur = score_kleur(score)
    circumference = 2 * 3.14159 * 45
    offset = circumference * (1 - score / 100)
    svg = f"""
    <div style="display:flex;flex-direction:column;align-items:center;padding:14px 0">
      <svg width="110" height="110" viewBox="0 0 110 110">
        <circle cx="55" cy="55" r="45" fill="none" stroke="#253047" stroke-width="9"/>
        <circle cx="55" cy="55" r="45" fill="none" stroke="{kleur}" stroke-width="9"
                stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                stroke-linecap="round" transform="rotate(-90 55 55)"/>
        <text x="55" y="60" text-anchor="middle" font-size="20" font-weight="700"
              fill="#F1F5F9" font-family="Inter,sans-serif">{score}%</text>
      </svg>
      <div style="font-size:12px;color:{kleur};font-weight:600;margin-top:4px">
        {score_label(score)}
      </div>
      <div style="font-size:10px;color:#8B9CB8;margin-top:2px">{label}</div>
    </div>
    """
    return svg


# ─────────────────────────────────────────────
# PERSONA KAART HTML
# ─────────────────────────────────────────────
def render_persona_card(p: dict) -> str:
    tags_html = "".join([f'<span class="pc-tag">{t}</span>' for t in p["tags"]])
    bronnen_html = "".join([f'<div class="xai-source">{b}</div>' for b in p["data_bronnen"]])
    factoren_html = "".join([f'<span class="xai-badge">{f}</span>' for f in p["sleutelfactoren"]])
    warn = "⚠️ " if p["kwaliteit"] == "slecht" else ""

    return f"""
    <div class="persona-card">
      <div style="display:flex;gap:16px;align-items:flex-start;margin-bottom:14px">
        <div style="width:64px;height:64px;border-radius:10px;background:#1f2d47;border:1px solid #2E3D5A;
                    display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;
                    color:#5B9BFF;flex-shrink:0">{warn}{p["initials"]}</div>
        <div style="flex:1">
          <div class="pc-name">{p["naam"]}</div>
          <div class="pc-diag">{p["geslacht"]} · {p["diagnose"]}</div>
          <div class="pc-quote">"{p["quote"]}"</div>
          <div>{tags_html}</div>
        </div>
        <div class="pc-age">{p["leeftijd"]} jr</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding-top:12px;border-top:1px solid #253047">
        <div style="display:flex;gap:8px"><span class="pc-det-label">📋 Context</span><span class="pc-det-val">{p["context"]}</span></div>
        <div style="display:flex;gap:8px"><span class="pc-det-label">🎯 Goals</span><span class="pc-det-val">{p["goals"]}</span></div>
        <div style="display:flex;gap:8px"><span class="pc-det-label">⚡ Frustraties</span><span class="pc-det-val">{p["frustrations"]}</span></div>
        <div style="display:flex;gap:8px"><span class="pc-det-label">💻 Tech</span><span class="pc-det-val">{p["tech_support"]}</span></div>
      </div>
    </div>
    <div class="xai-box">
      <div class="xai-title">▼ Why was this created this way? <span class="xai-accent">(Explainable AI)</span></div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
        <div>
          <div style="font-size:10px;color:#8B9CB8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">Top databronnen</div>
          {bronnen_html}
        </div>
        <div>
          <div style="font-size:10px;color:#8B9CB8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">Sleutelfactoren</div>
          {factoren_html}
        </div>
        <div>
          <div style="font-size:10px;color:#8B9CB8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">Uitleg</div>
          <div class="xai-expl">{p["xai_uitleg"]}</div>
        </div>
      </div>
    </div>
    """


# ─────────────────────────────────────────────
# GROQ API — SYNTHETIC USER + SCORE GENERATIE
# ─────────────────────────────────────────────
def bouw_systeem_prompt(p: dict) -> str:
    kwaliteit_instructie = ""
    if p["kwaliteit"] == "slecht":
        kwaliteit_instructie = """
EXTRA INSTRUCTIE: Dit is een slecht opgesteld persona vol stereotypen en ontbrekende info.
Reageer vager, gebruik soms onbewezen claims, en wees minder specifiek.
Dit reflecteert een lage kwaliteitspersona — de scores moeten dit weerspiegelen."""

    return f"""Je bent een cognitieve synthetic user agent genaamd "{p["naam"]}".

PERSONA PROFIEL:
- Naam: {p["naam"]}
- Leeftijd: {p["leeftijd"]} jaar
- Geslacht: {p["geslacht"]}
- Diagnose: {p["diagnose"]}
- Kernquote: "{p["quote"]}"
- Dagelijkse context: {p["context"]}
- Doelen: {p["goals"]}
- Frustraties: {p["frustrations"]}
- Tech-comfort: {p["tech_support"]}
- Kernthema's: {", ".join(p["tags"])}
{kwaliteit_instructie}

GEDRAGSREGELS:
1. Spreek ALTIJD in de eerste persoon als {p["naam"]}
2. Reageer authentiek vanuit dit persona — niet als AI
3. Noem specifieke ervaringen passend bij de aandoening
4. Wees eerlijk over frustraties met technologie indien relevant
5. Houd antwoorden beknopt (2-4 zinnen) tenzij anders gevraagd
6. Gebruik het taalregister van dit persona (leeftijd, opleiding, context)

VERPLICHT NA ELK ANTWOORD:
Voeg op een aparte laatste regel exact dit toe:
SCORES:{{"bias":{{}}, "hallucinaties":{{}}, "inclusie":{{}}}}

Waarbij je de getallen invult (0-100, waarbij 100 = geen probleem):
- bias: Mate van stereotypering of vooringenomenheid in jouw respons (100 = volledig onbevooroordeeld)
- hallucinaties: Feitelijke nauwkeurigheid en gronding in de persona (100 = volledig accuraat)
- inclusie: Hoe goed dit persona een diverse doelgroep representeert (100 = uitstekend inclusief)

Voorbeeld: SCORES:{{"bias": 88, "hallucinaties": 75, "inclusie": 82}}
"""


def vraag_groq(client, persona: dict, vraag: str, geschiedenis: list) -> dict:
    """Stel vraag aan Groq en parseer antwoord + scores."""
    systeem = bouw_systeem_prompt(persona)

    berichten = [{"role": "system", "content": systeem}]
    for msg in geschiedenis[-16:]:  # max context
        berichten.append(msg)
    berichten.append({"role": "user", "content": vraag})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=berichten,
            temperature=0.75,
            max_tokens=700,
        )
        volledig = response.choices[0].message.content.strip()

        # Parseer scores
        scores = {"bias": 75, "hallucinaties": 70, "inclusie": 65}
        import re
        match = re.search(r'SCORES:\s*(\{[^}]+\})', volledig)
        if match:
            try:
                raw = match.group(1)
                # Vervang Nederlandse sleutels indien nodig
                parsed = json.loads(raw)
                for k in ["bias", "hallucinaties", "inclusie"]:
                    if k in parsed and isinstance(parsed[k], (int, float)):
                        scores[k] = int(parsed[k])
            except Exception:
                pass

        # Verwijder scores-regel uit antwoord
        schoon = re.sub(r'\nSCORES:\s*\{[^}]+\}', '', volledig).strip()
        schoon = re.sub(r'SCORES:\s*\{[^}]+\}', '', schoon).strip()

        totaal = round((scores["bias"] + scores["hallucinaties"] + scores["inclusie"]) / 3)

        return {
            "tekst": schoon,
            "scores": {**scores, "totaal": totaal},
            "succes": True,
        }

    except Exception as e:
        return {
            "tekst": f"❌ Groq API fout: {str(e)}",
            "scores": {"bias": 0, "hallucinaties": 0, "inclusie": 0, "totaal": 0},
            "succes": False,
        }


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "actieve_persona_id" not in st.session_state:
    st.session_state.actieve_persona_id = 1
if "chatgeschiedenis" not in st.session_state:
    st.session_state.chatgeschiedenis = []
if "api_berichten" not in st.session_state:
    st.session_state.api_berichten = []
if "scores" not in st.session_state:
    st.session_state.scores = {"bias": 85, "hallucinaties": 62, "inclusie": 55, "totaal": 67}
if "persona_kaart_getoond" not in st.session_state:
    st.session_state.persona_kaart_getoond = False
if "rapport_open" not in st.session_state:
    st.session_state.rapport_open = False
if "berichtentelling" not in st.session_state:
    st.session_state.berichtentelling = 0


def get_actieve_persona():
    return next(p for p in PERSONAS if p["id"] == st.session_state.actieve_persona_id)


def wissel_persona(persona_id: int):
    if persona_id != st.session_state.actieve_persona_id:
        st.session_state.actieve_persona_id = persona_id
        st.session_state.chatgeschiedenis = []
        st.session_state.api_berichten = []
        st.session_state.persona_kaart_getoond = False
        st.session_state.berichtentelling = 0
        st.session_state.scores = {"bias": 85, "hallucinaties": 62, "inclusie": 55, "totaal": 67}


# ─────────────────────────────────────────────
# TOPBAR
# ─────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-logo">
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <rect width="28" height="28" rx="6" fill="#1a4fa0"/>
      <path d="M6 8h16M6 12h12M6 16h16M6 20h12" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
    Data Justice Assistent
  </div>
  <div style="margin-left:12px">
    <div class="topbar-project">ReumaNederland Project</div>
    <div class="topbar-sub">📚 ReumaNederland · Team 3</div>
  </div>
  <div style="margin-left:auto;display:flex;gap:10px;align-items:center">
    <span style="font-size:11px;color:#8B9CB8;background:#1a2438;border:1px solid #253047;border-radius:8px;padding:5px 12px">
      ⚖️ Mood checker
    </span>
    <span style="font-size:11px;color:#8B9CB8;background:#1a2438;border:1px solid #253047;border-radius:8px;padding:5px 12px">
      📋 Assign project
    </span>
    <span style="font-size:11px;color:white;background:#3B7EF6;border-radius:8px;padding:5px 14px;font-weight:600">
      ↑ Export
    </span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ Data Justice Assistent")
    st.markdown("---")

    client = get_groq_client()
    if client:
        st.markdown('<span style="color:#1DB87A;font-size:11px">✓ Groq verbonden (llama-3.3-70b)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#EF4444;font-size:11px">✗ Groq API key niet gevonden — zie README</span>', unsafe_allow_html=True)

    st.markdown("---")

    # Persona selectie
    st.markdown("### 👤 Persona's")
    st.markdown('<span style="font-size:10px;color:#8B9CB8">Research · ReumaNederland</span>', unsafe_allow_html=True)

    for p in PERSONAS:
        is_actief = p["id"] == st.session_state.actieve_persona_id
        kwaliteitskleur = "#EF4444" if p["kwaliteit"] == "slecht" else "#3B7EF6"
        rand_stijl = "rgba(59,126,246,.4)" if is_actief else "transparent"
        achtergrond = "rgba(59,126,246,.1)" if is_actief else "transparent"

        col_btn, _ = st.columns([1, 0.01])
        with col_btn:
            if st.button(
                f"{'✦ ' if is_actief else '  '}{p['naam']}  ·  {p['leeftijd']}jr",
                key=f"persona_btn_{p['id']}",
                use_container_width=True,
            ):
                wissel_persona(p["id"])
                st.rerun()

    st.markdown("---")

    col_edit, col_gen = st.columns(2)
    with col_edit:
        st.button("✏️ Edit", use_container_width=True)
    with col_gen:
        st.button("✨ Genereer", use_container_width=True)

    st.markdown("---")

    # Dataset
    st.markdown("### 🗃 Dataset")
    st.markdown("""
    <div style="background:#1a2438;border:1px solid #253047;border-radius:8px;
                padding:8px 12px;font-size:12px;color:#8B9CB8;margin-bottom:8px;display:flex;gap:8px">
      🗄 Dataset_ReumaNederland
    </div>
    """, unsafe_allow_html=True)
    st.button("📝 Edit Dataset", use_container_width=True)

    st.markdown("---")

    # Projecten
    st.markdown("### 📂 Projects")
    for proj in ["ReumaNederland", "Project 1", "Project 3"]:
        actief_proj = proj == "ReumaNederland"
        st.markdown(
            f'<div style="padding:6px 10px;border-radius:7px;font-size:12px;'
            f'background:{"rgba(59,126,246,.08)" if actief_proj else "transparent"};'
            f'color:{"#F1F5F9" if actief_proj else "#8B9CB8"};margin-bottom:3px">'
            f'📋 {proj}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Rapport knop
    if st.button("📊 Bekijk Validatierapport", use_container_width=True):
        st.session_state.rapport_open = not st.session_state.rapport_open

    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:#8B9CB8">👤 Designer · Greenberry<br>'
        '<span style="color:#3B7EF6">Groq llama-3.3-70b-versatile</span></div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# RAPPORT PANEEL (als uitgeklapt)
# ─────────────────────────────────────────────
actieve_p = get_actieve_persona()
scores = st.session_state.scores

if st.session_state.rapport_open:
    st.markdown("---")
    st.markdown("### 📊 Validation & Risk Overview")

    col_ring, col_checks, col_verbeter = st.columns([1, 1.5, 1.5])

    with col_ring:
        st.markdown(teken_score_ring(scores["totaal"], "Totaalscore"), unsafe_allow_html=True)

    with col_checks:
        st.markdown("**Checks**")
        for naam, key in [("Bias check", "bias"), ("Hallucinatie check", "hallucinaties"), ("Data Justice check", "inclusie")]:
            s = scores[key]
            kleur = score_kleur(s)
            lbl = score_label(s)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                f'border-bottom:1px solid #253047;font-size:12px">'
                f'<span style="color:#8B9CB8">{naam}</span>'
                f'<span style="color:{kleur};font-weight:600">{s}% — {lbl}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:8px 0;font-size:12px">'
            f'<span style="color:#8B9CB8">Totaalscore</span>'
            f'<span style="color:{score_kleur(scores["totaal"])};font-weight:700">{scores["totaal"]}%</span></div>',
            unsafe_allow_html=True,
        )

    with col_verbeter:
        st.markdown("**Verbeter AI input**")
        verbeterpunten = [
            ("📋 Voeg context toe", "Verbeter relevantie"),
            ("🔑 Verfijn prompt", "Betere resultaten"),
            ("📋 Check datakwaliteit", "Review dataset"),
            ("⚠ Meld een probleem", "Help ons verbeteren"),
        ]
        for naam, actie in verbeterpunten:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:7px 0;'
                f'border-bottom:1px solid #253047;font-size:11px">'
                f'<span style="color:#F1F5F9">{naam}</span>'
                f'<span style="color:#8B9CB8">{actie}</span></div>',
                unsafe_allow_html=True,
            )

    col_fix, col_export = st.columns(2)
    with col_fix:
        st.button("🔧 Fix issues", use_container_width=True)
    with col_export:
        if st.button("📤 Export rapport", use_container_width=True):
            rapport_data = {
                "persona": actieve_p["naam"],
                "scores": st.session_state.scores,
                "chatgeschiedenis": st.session_state.chatgeschiedenis,
            }
            st.download_button(
                "⬇ Download JSON",
                data=json.dumps(rapport_data, indent=2, ensure_ascii=False),
                file_name=f"data_justice_rapport_{actieve_p['naam'].replace(' ', '_')}.json",
                mime="application/json",
            )
    st.markdown("---")


# ─────────────────────────────────────────────
# CHAT WEERGAVE
# ─────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    for bericht in st.session_state.chatgeschiedenis:
        if bericht["rol"] == "assistent":
            st.markdown(f"""
            <div class="msg-wrap-bot">
              <div class="msg-time">{bericht.get("tijd", "")}</div>
              <div class="msg-sender">🤖 Synthetic User · {actieve_p["naam"]}</div>
              <div class="bubble-bot">{bericht["inhoud"]}</div>
            </div>
            """, unsafe_allow_html=True)

            if bericht.get("toon_persona_kaart"):
                st.markdown(render_persona_card(actieve_p), unsafe_allow_html=True)

        elif bericht["rol"] == "gebruiker":
            st.markdown(f"""
            <div class="msg-wrap-user">
              <div class="msg-time">{bericht.get("tijd", "")}</div>
              <div class="bubble-user">{bericht["inhoud"]}</div>
            </div>
            """, unsafe_allow_html=True)

        elif bericht["rol"] == "systeem":
            st.markdown(f"""
            <div class="msg-wrap-bot">
              <div class="msg-sender">⚖️ Data Justice Assistent</div>
              <div class="bubble-bot">{bericht["inhoud"]}</div>
            </div>
            """, unsafe_allow_html=True)


# Welkomstbericht bij lege chat
if not st.session_state.chatgeschiedenis:
    st.markdown(f"""
    <div class="msg-wrap-bot">
      <div class="msg-time">Nu</div>
      <div class="msg-sender">⚖️ Data Justice Assistent</div>
      <div class="bubble-bot">
        Hallo! Ik ben de <strong>Data Justice Assistent</strong>.<br><br>
        Actieve synthetic user: <strong>{actieve_p["naam"]}</strong> ({actieve_p["leeftijd"]}jr, {actieve_p["diagnose"]}).<br><br>
        Stel een vraag om de conversatie te starten. Elk antwoord wordt real-time geëvalueerd op
        <strong>bias</strong>, <strong>hallucinaties</strong> en <strong>inclusie</strong>.
        {'<br><br>⚠️ <span style="color:#F59E0B">Let op: dit persona heeft bekende kwaliteitsproblemen — ideaal om bias-detectie te testen!</span>' if actieve_p["kwaliteit"] == "slecht" else ""}
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# RELIABILITY BAR
# ─────────────────────────────────────────────
def render_reliability_bar(scores: dict) -> str:
    b, h, i = scores["bias"], scores["hallucinaties"], scores["inclusie"]

    def badge(s, lbl):
        if s >= 80:
            return f'<span class="rel-badge-green">✓ {lbl} — Laag</span>'
        elif s >= 60:
            return f'<span class="rel-badge-amber">⚠ {lbl} — Medium</span>'
        return f'<span class="rel-badge-red">✗ {lbl} — Hoog</span>'

    return f"""
    <div class="rel-bar">
      <span class="rel-label">ⓘ Reliability:</span>
      {badge(h, "Hallucinaties")}
      {badge(b, "Bias")}
      {badge(i, "Data Justice")}
      <span style="margin-left:auto;font-size:11px;color:#3B7EF6;cursor:pointer">View Full Report &gt;&gt;</span>
    </div>
    """


st.markdown(render_reliability_bar(scores), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INPUT FORMULIER
# ─────────────────────────────────────────────
st.markdown("---")

with st.form("chat_form", clear_on_submit=True):
    col_spark, col_input, col_btn = st.columns([0.05, 1, 0.12])

    with col_spark:
        st.markdown('<div style="font-size:22px;color:#3B7EF6;padding-top:6px">✦</div>', unsafe_allow_html=True)

    with col_input:
        gebruiker_vraag = st.text_input(
            "Vraag",
            placeholder="Ask the Synthetic User...",
            label_visibility="collapsed",
        )

    with col_btn:
        versturen = st.form_submit_button("Send ➤", use_container_width=True)


# ─────────────────────────────────────────────
# BERICHTVERWERKING
# ─────────────────────────────────────────────
if versturen and gebruiker_vraag.strip():
    if not client:
        st.error("⚠️ Voer eerst een geldige Groq API key in de sidebar in.")
    else:
        nu = time.strftime("%H:%M")
        actieve_p = get_actieve_persona()

        # Sla gebruikersbericht op
        st.session_state.chatgeschiedenis.append({
            "rol": "gebruiker",
            "inhoud": gebruiker_vraag.strip(),
            "tijd": nu,
        })

        # Eerste bericht: toon persona-kaart intro
        eerste_bericht = st.session_state.berichtentelling == 0

        with st.spinner("Synthetic User denkt na..."):
            resultaat = vraag_groq(
                client,
                actieve_p,
                gebruiker_vraag.strip(),
                st.session_state.api_berichten,
            )

        # Update API-geschiedenis
        st.session_state.api_berichten.append(
            {"role": "user", "content": gebruiker_vraag.strip()}
        )
        st.session_state.api_berichten.append(
            {"role": "assistant", "content": resultaat["tekst"]}
        )

        # Sla antwoord op
        st.session_state.chatgeschiedenis.append({
            "rol": "assistent",
            "inhoud": resultaat["tekst"],
            "tijd": nu,
            "toon_persona_kaart": eerste_bericht,
        })

        # Update scores
        if resultaat["succes"]:
            st.session_state.scores = resultaat["scores"]

        st.session_state.berichtentelling += 1
        st.rerun()


# ─────────────────────────────────────────────
# SCORE DETAIL SECTIE (altijd zichtbaar na gesprek)
# ─────────────────────────────────────────────
if st.session_state.berichtentelling > 0:
    with st.expander("📈 Score detail — laatste evaluatie", expanded=False):
        col_b, col_h, col_i, col_t = st.columns(4)
        score_data = [
            (col_b, scores["bias"], "Bias", "Mate van stereotypering"),
            (col_h, scores["hallucinaties"], "Hallucinaties", "Feitelijke nauwkeurigheid"),
            (col_i, scores["inclusie"], "Inclusie", "Representativiteit"),
            (col_t, scores["totaal"], "Totaal", "Gecombineerde score"),
        ]
        for col, val, naam, beschr in score_data:
            with col:
                kleur = score_kleur(val)
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-val" style="color:{kleur}">{val}%</div>'
                    f'<div class="metric-lbl">{naam}</div>'
                    f'<div style="font-size:9px;color:#8B9CB8;margin-top:3px">{beschr}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("""
        <div style="margin-top:14px;padding:12px;background:#1a2438;border:1px solid #253047;border-radius:8px;font-size:11px;color:#8B9CB8">
          <strong style="color:#5B9BFF">Scoringsmethode (LangGraph-geïnspireerd):</strong><br>
          De synthetic user genereert zelf een score op basis van zijn eigen respons.
          Bias = vrijheid van stereotypen; Hallucinaties = feitelijke gronding in het persona;
          Inclusie = hoe goed de respons een diverse doelgroep vertegenwoordigt.
          Scores worden berekend door llama-3.3-70b-versatile en zijn indicatief.
        </div>
        """, unsafe_allow_html=True)

    # Export knop
    if st.button("📥 Download gesprek (JSON)"):
        export = {
            "project": "ReumaNederland",
            "persona": {
                "naam": actieve_p["naam"],
                "leeftijd": actieve_p["leeftijd"],
                "diagnose": actieve_p["diagnose"],
            },
            "laatste_scores": st.session_state.scores,
            "chatgeschiedenis": [
                {"rol": m["rol"], "inhoud": m["inhoud"]}
                for m in st.session_state.chatgeschiedenis
            ],
        }
        st.download_button(
            label="⬇ Download",
            data=json.dumps(export, indent=2, ensure_ascii=False),
            file_name=f"data_justice_{actieve_p['naam'].replace(' ', '_')}.json",
            mime="application/json",
        )
