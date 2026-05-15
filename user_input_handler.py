
import os
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# !pip install langchain-groq
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY'] = "jouw_groq_api_key_hier"

# temperature=0.8 voor variatie in de persona's
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.8)

print("✅ Groq verbinding klaar")

# --- SCHEMA'S ---
# Pydantic BaseModel dwingt het model altijd exact deze velden terug te geven.

# Schema voor één validatiecheck: score + toelichting
class CheckSchema(BaseModel):
    score: int = Field(description="Score van 0 tot 100")
    toelichting: str = Field(description="Maximaal één zin uitleg bij de score")

# Hoofdschema voor een volledige persona-analyse
class PersonaSchema(BaseModel):
    naam: str = Field(description="Naam van de persona")
    samenvatting: str = Field(description="Korte neutrale beschrijving van de persona")
    kenmerken: list[str] = Field(description="Lijst van gedragskenmerken of eigenschappen")
    bias:          CheckSchema = Field(description="Bias-check: zijn er stereotypen of vooroordelen?")
    hallucinaties: CheckSchema = Field(description="Hallucinatie-check: zijn claims onderbouwd?")
    inclusie:      CheckSchema = Field(description="Inclusie-check: is de persona representatief en respectvol?")
    totaalscore:   int         = Field(description="Gemiddelde van de drie scores (afgerond)")

print("✅ Schema's klaar")

"""Hieronder staat de prompt waar de agent zich aan moet houden. Hier heb ik meerdere variaties mee geprobeerd, echter schreef Xu et al. (2025) over de combinatie van bias, hallucinatie en data justice. Data justice heb nu verwerkt als inclusie."""

# --- PROMPT TEMPLATE ---
# De assistent is een Bias-Justice validator voor UX-onderzoekers.
# Hij analyseert synthetic persona's op drie lagen en geeft concrete scores.

prompt = ChatPromptTemplate.from_messages([
    ("human", """### Wie ben je
Jij bent een Bias-Justice validator gespecialiseerd in het beoordelen van synthetische
UX-persona's. Je analyseert persona's op drie criteria en geeft eerlijke, onderbouwde scores.

Je werkt altijd systematisch:
- Je beoordeelt BIAS: zijn er stereotypen, vooroordelen of eenzijdige aannames?
- Je beoordeelt HALLUCINATIES: zijn de beschreven kenmerken realistisch en verifieerbaar?
- Je beoordeelt INCLUSIE: vertegenwoordigt de persona diverse perspectieven respectvol?

Scoreschaal:
- 0–70  = problematisch (rood)
- 71–80 = aandacht nodig (geel)
- 81–100 = goed (groen)

### De persona
{persona}

### Jouw taak
Analyseer de persona en geef:
1. Een neutrale samenvatting van wie deze persona is
2. Een lijst van geïdentificeerde kenmerken
3. Een score + toelichting voor bias, hallucinaties en inclusie
4. Een totaalscore (gemiddelde van de drie, afgerond)

### Regels
- Wees specifiek in je toelichting — geen vage uitspraken
- Geef altijd een concrete reden voor de score
- Wees eerlijk: ook goed geschreven persona's kunnen bias bevatten

### Output (JSON)
{{
  "naam": "naam van de persona",
  "samenvatting": "neutrale beschrijving",
  "kenmerken": ["kenmerk 1", "kenmerk 2"],
  "bias":          {{"score": 0-100, "toelichting": "..."}},
  "hallucinaties": {{"score": 0-100, "toelichting": "..."}},
  "inclusie":      {{"score": 0-100, "toelichting": "..."}},
  "totaalscore":   0-100
}}
""")
])

print("✅ Prompt geladen — Bias-Justice validator klaar")

# ============================================================
# CEL 4a: PERSONA GENERATOR
# ============================================================
# Geef hier op hoeveel persona's je wilt per doelgroep.
# Het LLM bedenkt ze automatisch — jij hoeft niets handmatig in te typen.

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate # Added this import

# --- SCHEMA voor één gegenereerde persona ---
class GegenereerdePersona(BaseModel):
    naam:        str       = Field(description="Volledige naam van de persona")
    doelgroep:   str       = Field(description="Doelgroep waartoe deze persona behoort")
    leeftijd:    int       = Field(description="Leeftijd in jaren")
    achtergrond: str       = Field(description="2-3 zinnen over wie deze persoon is")
    uitdagingen: list[str] = Field(description="2-4 concrete uitdagingen of behoeften")
    gedrag:      list[str] = Field(description="2-4 gedragskenmerken relevant voor UX")

class PersonaSetSchema(BaseModel):
    personas: list[GegenereerdePersona] = Field(description="Lijst van gegenereerde persona's")

# --- OPDRACHT: pas dit aan naar jouw wensen ---
OPDRACHT = """
Genereer de volgende synthetische UX-persona's voor een digitaal zorgplatform:
- 3 reumapatiënten (gevarieerd in leeftijd, achtergrond en digitale vaardigheid)
- 1 zorgpersoneel (verpleegkundige of arts)
- 1 UX designer (gespecialiseerd in inclusief ontwerp)

Maak elke persona realistisch en specifiek. Vermijd stereotypen.
Zorg voor diversiteit in leeftijd, geslacht, culturele achtergrond en digitale vaardigheid.
"""

# --- GENEREER ---
genereer_prompt = ChatPromptTemplate.from_messages([
    ("human", """Je bent een expert in het ontwerpen van inclusieve UX-persona's.
Genereer persona's op basis van deze opdracht:

{opdracht}

Regels:
- Elke persona is uniek en specifiek (geen vage algemeenheden)
- Gevarieerd in leeftijd, geslacht en culturele achtergrond
- Uitdagingen zijn concreet en verifieerbaar
- Geen stereotypen of vooroordelen

Geef ALLEEN een JSON object terug:
{{"personas": [
  {{"naam": "...", "doelgroep": "...", "leeftijd": 0,
    "achtergrond": "...", "uitdagingen": ["..."], "gedrag": ["..."]}}
]}}
""")
])

print("⏳ Persona's genereren...")
structured_llm = llm.with_structured_output(PersonaSetSchema, method="json_mode")
chain = genereer_prompt | structured_llm
resultaat = chain.invoke({"opdracht": OPDRACHT})

# --- OMZETTEN NAAR EVALUATIESET ---
# Elke persona wordt omgezet naar een leesbare tekst, net als handmatig ingevoerde persona's
def persona_naar_tekst(p: GegenereerdePersona) -> str:
    uitdagingen = "\n".join(f"- {u}" for u in p.uitdagingen)
    gedrag       = "\n".join(f"- {g}" for g in p.gedrag)
    return (
        f"{p.naam}, {p.leeftijd} jaar, {p.doelgroep}\n"
        f"{p.achtergrond}\n"
        f"Uitdagingen:\n{uitdagingen}\n"
        f"Gedrag:\n{gedrag}"
    )

evaluatieset = [
    (p.naam, persona_naar_tekst(p))
    for p in resultaat.personas
]

print(f"✅ {len(evaluatieset)} persona's gegenereerd:\n")
for naam, tekst in evaluatieset:
    print(f"  → {naam}")
    print(f"    {tekst.splitlines()}...\n")

# """Hierboven worden de vijf verschillende persona's gecreeerd, waaronder 1 ux designer, 1 zorgpersoneel en 3 reumapatienten. Ze krijgen een naam, leeftijd, culturele achtergrond, digitale vaardigheid, uitdagingen en gedrag"""

# De evaluatieset wordt nu automatisch aangemaakt door cel 4a hierboven.
# Je hoeft hier niets meer te doen — scroll omhoog en pas de OPDRACHT aan.
print(f"✅ Evaluatieset klaar: {len(evaluatieset)} persona's geladen")

# ============================================================
# LANGGRAPH WORKFLOW
# ============================================================
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
import json, csv

# STATE
class PersonaState(TypedDict):
    persona_tekst:    str
    persona_schema:   Optional[dict]
    validatie_fouten: list
    reparatie_pogingen: int
    export_pad:       Optional[str]


# NODE 1: PARSE
def parse_persona(state: PersonaState) -> dict:
    print("  ▶ Node 1: Parsen...")
    structured_llm = llm.with_structured_output(PersonaSchema, method="json_mode")
    chain = prompt | structured_llm
    response = chain.invoke({"persona": state["persona_tekst"]})
    return {"persona_schema": response.model_dump()}


# NODE 2: VALIDEER
def valideer_persona(state: PersonaState) -> dict:
    print("  ▶ Node 2: Valideren...")
    fouten = []
    schema = state["persona_schema"]

    if not schema.get("naam"):
        fouten.append("Naam ontbreekt")
    if not schema.get("samenvatting") or len(schema["samenvatting"]) < 10:
        fouten.append("Samenvatting te kort")
    if not schema.get("kenmerken") or len(schema["kenmerken"]) < 2:
        fouten.append("Minder dan 2 kenmerken")
    for check in ["bias", "hallucinaties", "inclusie"]:
        if not schema.get(check) or schema[check].get("score") is None:
            fouten.append(f"Score ontbreekt voor {check}")
        if not schema.get(check) or not schema[check].get("toelichting"):
            fouten.append(f"Toelichting ontbreekt voor {check}")
    if schema.get("totaalscore") is None:
        fouten.append("Totaalscore ontbreekt")

    if fouten:
        print(f"  ⚠ Fouten: {fouten}")
    else:
        print("  ✓ Validatie geslaagd")
    return {"validatie_fouten": fouten}


# CONDITIE
def bepaal_volgende_stap(state: PersonaState) -> str:
    if state["validatie_fouten"] and state["reparatie_pogingen"] < 2:
        return "repareer"
    return "exporteer"


# NODE 3: REPAREER
def repareer_persona(state: PersonaState) -> dict:
    pogingen = state["reparatie_pogingen"] + 1
    print(f"  ▶ Node 3: Repareren (poging {pogingen})...")
    repareer_prompt = ChatPromptTemplate.from_messages([
        ("human", """Het persona-schema heeft fouten. Verbeter het als Bias-Justice validator.
Huidig schema: {schema}
Fouten: {fouten}
Originele tekst: {persona_tekst}
Geef verbeterd JSON terug met alle vereiste velden:
{{
  "naam": "...",
  "samenvatting": "...",
  "kenmerken": ["..."],
  "bias":          {{"score": 0-100, "toelichting": "..."}},
  "hallucinaties": {{"score": 0-100, "toelichting": "..."}},
  "inclusie":      {{"score": 0-100, "toelichting": "..."}},
  "totaalscore":   0-100
}}
""")
    ])
    structured_llm = llm.with_structured_output(PersonaSchema, method="json_mode")
    chain = repareer_prompt | structured_llm
    response = chain.invoke({
        "schema":       json.dumps(state["persona_schema"], ensure_ascii=False),
        "fouten":       "\n".join(state["validatie_fouten"]),
        "persona_tekst": state["persona_tekst"]
    })
    return {"persona_schema": response.model_dump(), "reparatie_pogingen": pogingen, "validatie_fouten": []}


# NODE 4: EXPORTEER (JSON per persona)
def exporteer_persona(state: PersonaState) -> dict:
    print("  ▶ Node 4: Exporteren...")
    naam = state["persona_schema"]["naam"][:30].replace(" ", "_").replace("/", "-")
    pad  = f"persona_{naam}.json"
    with open(pad, "w", encoding="utf-8") as f:
        json.dump(state["persona_schema"], f, indent=2, ensure_ascii=False)
    return {"export_pad": pad}


# GRAPH BOUWEN
workflow = StateGraph(PersonaState)
workflow.add_node("parse",     parse_persona)
workflow.add_node("valideer",  valideer_persona)
workflow.add_node("repareer",  repareer_persona)
workflow.add_node("exporteer", exporteer_persona)
workflow.add_edge(START, "parse")
workflow.add_edge("parse", "valideer")
workflow.add_conditional_edges("valideer", bepaal_volgende_stap, {"repareer": "repareer", "exporteer": "exporteer"})
workflow.add_edge("repareer", "valideer")
workflow.add_edge("exporteer", END)
app = workflow.compile()
print("✅ LangGraph workflow klaar!\n")


# ============================================================
# UITVOEREN OP EVALUATIESET
# ============================================================
def kleur_label(score: int) -> str:
    if score <= 70:  return "🔴 ROOD"
    if score <= 80:  return "🟡 GEEL"
    return "🟢 GROEN"

personas_output = []

for naam, persona in evaluatieset:
    print(f"{'='*50}")
    print(f"Verwerken: {naam}")
    resultaat = app.invoke({
        "persona_tekst":      persona,
        "persona_schema":     None,
        "validatie_fouten":   [],
        "reparatie_pogingen": 0,
        "export_pad":         None
    })
    schema = resultaat["persona_schema"]
    schema["reparatie_pogingen"] = resultaat["reparatie_pogingen"]
    personas_output.append(schema)

    b = schema["bias"]
    h = schema["hallucinaties"]
    i = schema["inclusie"]
    print(f"  Bias:          {b['score']:>3}%  {kleur_label(b['score'])}  — {b['toelichting']}")
    print(f"  Hallucinaties: {h['score']:>3}%  {kleur_label(h['score'])}  — {h['toelichting']}")
    print(f"  Inclusie:      {i['score']:>3}%  {kleur_label(i['score'])}  — {i['toelichting']}")
    print(f"  Totaalscore:   {schema['totaalscore']:>3}%  {kleur_label(schema['totaalscore'])}")


# ============================================================
# CSV EXPORT
# ============================================================
csv_pad = "personas_evaluatie.csv"
with open(csv_pad, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "naam", "samenvatting", "kenmerken",
        "bias_score", "bias_toelichting",
        "hallucinaties_score", "hallucinaties_toelichting",
        "inclusie_score", "inclusie_toelichting",
        "totaalscore", "reparatie_pogingen"
    ])
    for r in personas_output:
        writer.writerow([
            r["naam"],
            r["samenvatting"],
            " | ".join(r["kenmerken"]),
            r["bias"]["score"],          r["bias"]["toelichting"],
            r["hallucinaties"]["score"], r["hallucinaties"]["toelichting"],
            r["inclusie"]["score"],      r["inclusie"]["toelichting"],
            r["totaalscore"],
            r["reparatie_pogingen"]
        ])

# ============================================================
# JSON EXPORT
# ============================================================
json_pad = "personas_evaluatie.json"
with open(json_pad, "w", encoding="utf-8") as f:
    json.dump(personas_output, f, indent=2, ensure_ascii=False)

print(f"\n{'='*50}")
print(f"✅ Evaluatie compleet!")
print(f"   {len(personas_output)} persona's verwerkt")
print(f"   📄 CSV:  {csv_pad}")
print(f"   📦 JSON: {json_pad}")

"""### Interactie met een Persona-Chatbot

Nu kunnen we een chatbot toevoegen die antwoorden geeft vanuit het perspectief van een van de gegenereerde persona's. Dit kan nuttig zijn om te begrijpen hoe een specifieke gebruiker zou reageren op vragen of scenario's.
"""

# ============================================================
# CHATBOT MET PERSONA INTERACTIE
# ============================================================

# Controleer of 'personas_output' is gedefinieerd en gevuld
if 'personas_output' not in locals() or not personas_output:
    print("❌ Fout: De 'personas_output' lijst is niet gevonden of is leeg.")
    print("       Zorg ervoor dat de voorgaande cel ('cell_5_workflow') volledig is uitgevoerd.")
else:
    # Selecteer een van de gegenereerde persona's om als te fungeren
    # Voor dit voorbeeld gebruiken we de eerste persona in de lijst.
    # In een echte toepassing kun je de gebruiker laten kiezen of willekeurig selecteren.
    selected_persona_data = personas_output[0]

    # Creëer een gedetailleerde beschrijving van de geselecteerde persona
    # Dit zal gebruikt worden in de systeeminstructie van de chatbot
    persona_description = f"""
Je bent {selected_persona_data['naam']}. Hier zijn jouw kenmerken en uitdagingen:
- Samenvatting: {selected_persona_data['samenvatting']}
- Kenmerken: {', '.join(selected_persona_data['kenmerken'])}
- Bias Score: {selected_persona_data['bias']['score']}% - {selected_persona_data['bias']['toelichting']}
- Hallucinatie Score: {selected_persona_data['hallucinaties']['score']}% - {selected_persona_data['hallucinaties']['toelichting']}
- Inclusie Score: {selected_persona_data['inclusie']['score']}% - {selected_persona_data['inclusie']['toelichting']}
"""

    # Prompt template voor de chatbot, inclusief de persona beschrijving
    chatbot_prompt = ChatPromptTemplate.from_messages([
        ("system", f"Jij bent een AI-assistent die antwoordt als de volgende persona:\n\n{persona_description}\n\nAntwoord altijd vanuit het perspectief van deze persona. Houd rekening met de leeftijd, achtergrond, uitdagingen en gedragskenmerken van de persona. Wees beknopt en direct."),
        ("human", "{question}")
    ])

    # Creëer de chatbot keten
    chatbot_chain = chatbot_prompt | llm

    print(f"✅ Chatbot geladen. Ik beantwoord nu vragen als: {selected_persona_data['naam']}\n")
    print("Stel een vraag (typ 'stop' om te stoppen):\n")

    while True:
        user_question = input("Jouw vraag: ")
        if user_question.lower() == 'stop':
            break

        response = chatbot_chain.invoke({"question": user_question})
        print(f"{selected_persona_data['naam']}: {response.content}\n")

    print("Chatbot sessie beëindigd.")

"""Wij eindigen met de vijf persona's die ieder een score krijgen op bias, hallucinaties, inclusie en een totaalscore voor een snel overzicht. Dit zou ik aan de virtuele assistent kunnen koppelen, zodat die de synthetic user 24/7 controleert en de designer kan waarschuwen zodra het geel of zelfs rood wordt en daarvoor ook aanpassingen kan voorstellen.

Dit is waar ik zeker mee aan de slag wil gaan in het volgende blok, evenals het visueel maken in streamlit of door middel van andere programeer talen zoals: html, css en js.

Volgende blok wil ik ook de data gaan gebruiken die we hebben gekregen van de klant, echter is de dataset niet enorm groot waardoor ik blok c en het testen met een croq api key heb gedaan.

Zelf merk ik dat Blok C het eerste blok is waarbij ik merk dat het steeds leuker wordt om met de code te spelen en gewoon wat te proberen.
"""

