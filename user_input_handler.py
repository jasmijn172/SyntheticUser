
import json, csv
import os
from langgraph.graph import StateGraph, START, END
import streamlit as st
from typing import Optional, TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# !pip install langchain-groq
from langchain_groq import ChatGroq




# ============================================================
# AI GENERATION SCHEMA'S
# ============================================================
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


class PersonaState(TypedDict):
    persona_tekst:    str
    persona_schema:   Optional[dict]
    validatie_fouten: list
    reparatie_pogingen: int
    export_pad:       Optional[str]


# ============================================================
# MAIN CLASS VOOR HET AFHANDELEN VAN GEBRUIKERSINPUT EN AI-INTERACTIES
# ============================================================
class UserInputHandler:
    def __init__(self, persona_name: str):

        # Init ai variables
        self.__init_ai__()
        self.persona_name = persona_name

    def __init_ai__(self):
        os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.8)

    def get_strutured_llm(self, schema):
        return self.llm.with_structured_output(schema, method="json_mode")

    # ============================================================
    # PERSONA MANAGEMENT FUNCTIES
    # ============================================================

    def get_persona_name(self):
        return self.persona_name 

    def get_persona_dir_path(self) -> str:
        return "./personas/"

    def load_personas(self):
        # Deze functie zal later worden ingevuld met de logica om persona's te laden
        pass

    def get_persona_by_name(self, name: str):
        # Deze functie zal later worden ingevuld met de logica om een specifieke persona op te halen
        pass

    def generate_personas(self):
        # Deze functie zal later worden ingevuld met de logica om nieuwe persona's te genereren
        pass

    
    def get_bias_justice_validator(self):
        return ChatPromptTemplate.from_messages([
            ("human", 
             """### Wie ben je
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


    def get_persona_generator_prompt(self):
        return """
        Genereer de volgende synthetische UX-persona voor een digitaal zorgplatform:
        - 1 reumapatiënt (gevarieerd in leeftijd, achtergrond en digitale vaardigheid)

        Maak deze persona realistisch en specifiek. Vermijd stereotypen.
        Zorg voor diversiteit in leeftijd, geslacht, culturele achtergrond en digitale vaardigheid.
        """
    
    def generate_persona(self):

        opdracht = self.get_persona_generator_prompt()

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
        
        structured_llm = self.get_strutured_llm(PersonaSetSchema)
        chain = genereer_prompt | structured_llm
        resultaat = chain.invoke({"opdracht": opdracht})

        

        return resultaat

    def persona_naar_tekst(self, p: GegenereerdePersona) -> str:
        # Elke persona wordt omgezet naar een leesbare tekst, net als handmatig ingevoerde persona's

        uitdagingen = "\n".join(f"- {u}" for u in p.uitdagingen)
        gedrag       = "\n".join(f"- {g}" for g in p.gedrag)
        return (
            f"{p.naam}, {p.leeftijd} jaar, {p.doelgroep}\n"
            f"{p.achtergrond}\n"
            f"Uitdagingen:\n{uitdagingen}\n"
            f"Gedrag:\n{gedrag}"
        )

    def generate_evaluation_set(self):

        evaluatieset = [
            (p.naam, self.persona_naar_tekst(p))
            for p in resultaat.personas
        ]

        print(f"✅ {len(evaluatieset)} persona's gegenereerd:\n")
        for naam, tekst in evaluatieset:
            print(f"  → {naam}")
            print(f"    {tekst.splitlines()}...\n")


    # NODE 1: PARSE
    def parse_persona(self, state: PersonaState) -> dict:
        print("  ▶ Node 1: Parsen...")
        structured_llm = self.get_strutured_llm(PersonaSchema)
        chain = get_bias_justice_validator() | structured_llm
        response = chain.invoke({"persona": state["persona_tekst"]})
        return {"persona_schema": response.model_dump()}


    # NODE 2: VALIDEER
    def valideer_persona(self, state: PersonaState) -> dict:
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
    def bepaal_volgende_stap(self, state: PersonaState) -> str:
        if state["validatie_fouten"] and state["reparatie_pogingen"] < 2:
            return "repareer"
        return "exporteer"


    # NODE 3: REPAREER
    def repareer_persona(self, state: PersonaState) -> dict:
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

        structured_llm = self.get_strutured_llm(PersonaSchema)
        chain = repareer_prompt | structured_llm

        response = chain.invoke({
            "schema":       json.dumps(state["persona_schema"], ensure_ascii=False),
            "fouten":       "\n".join(state["validatie_fouten"]),
            "persona_tekst": state["persona_tekst"]
        })
        return {"persona_schema": response.model_dump(), "reparatie_pogingen": pogingen, "validatie_fouten": []}


    # NODE 4: EXPORTEER (JSON per persona)
    def exporteer_persona(self, state: PersonaState) -> dict:
        print("  ▶ Node 4: Exporteren...")

        naam = state["persona_schema"]["naam"][:30].replace(" ", "_").replace("/", "-")

        pad  = self.get_persona_dir_path() + f"persona_{naam}.json"

        with open(pad, "w", encoding="utf-8") as f:
            json.dump(state["persona_schema"], f, indent=2, ensure_ascii=False)
        return {"export_pad": pad}

    def build_graph(self):
        # GRAPH BOUWEN
        workflow = StateGraph(PersonaState)
        workflow.add_node("parse",     self.parse_persona)
        workflow.add_node("valideer",  self.valideer_persona)
        workflow.add_node("repareer",  self.repareer_persona)
        workflow.add_node("exporteer", self.exporteer_persona)
        workflow.add_edge(START, "parse")
        workflow.add_edge("parse", "valideer")
        workflow.add_conditional_edges("valideer", self.bepaal_volgende_stap, {"repareer": "repareer", "exporteer": "exporteer"})
        workflow.add_edge("repareer", "valideer")
        workflow.add_edge("exporteer", END)
        return workflow.compile()


    def generate_persona_evaluations(self):
        #load into directory
        #read all personas
        #process personas
        #create file

        os.listdir(self.get_persona_dir_path())
        evaluatieset = []
        for bestand in os.listdir(self.get_persona_dir_path()):
            if bestand.endswith(".json"):
                with open(self.get_persona_dir_path() + bestand, "r", encoding="utf-8") as f:
                    persona = json.load(f)
                    evaluatieset.append(self.process_persona(json.dumps(persona, ensure_ascii=False)))

        self.write_csv_file(evaluatieset)
        self.write_json_file(evaluatieset)
        


    def process_persona(self, persona) -> dict:

        resultaat = self.build_graph().invoke({
            "persona_tekst":      persona,
            "persona_schema":     None,
            "validatie_fouten":   [],
            "reparatie_pogingen": 0,
            "export_pad":         None
        })

        schema = resultaat["persona_schema"]
        schema["reparatie_pogingen"] = resultaat["reparatie_pogingen"]

        return schema


    def write_csv_file(self):
        # ============================================================
        # CSV EXPORT
        # ============================================================
        csv_pad = self.get_persona_dir_path() + "personas_evaluatie.csv"
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

    def write_json_file(self):
        # ============================================================
        # JSON EXPORT
        # ============================================================
        json_pad = self.get_persona_dir_path() + "personas_evaluatie.json"
        with open(json_pad, "w", encoding="utf-8") as f:
            json.dump(personas_output, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*50}")
        print(f"✅ Evaluatie compleet!")
        print(f"   {len(personas_output)} persona's verwerkt")
        print(f"   📄 CSV:  {csv_pad}")
        print(f"   📦 JSON: {json_pad}")

        return personas_output


    # ============================================================
    # UITVOEREN OP EVALUATIESET
    # ============================================================
    def kleur_label(self, score: int) -> str:
        if score <= 70:  return "🔴 ROOD"
        if score <= 80:  return "🟡 GEEL"
        return "🟢 GROEN"


    # ============================================================
    # CHATBOT MET PERSONA INTERACTIE
    # ============================================================
    def ask_persona(self, question: str) -> str:
        # Deze functie zal later worden ingevuld met de chatbot logica

        personas_output = self.generate_persona_evaluations()

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
                ("human", "{user_input}")
            ])

            # Creëer de chatbot keten
            chatbot_chain = chatbot_prompt | llm

            ps_response = chatbot_chain.invoke({"user_input": question})


            print(f"✅ Chatbot geladen. Ik beantwoord nu vragen als: {selected_persona_data['naam']}\n")
            print("Stel een vraag (typ 'stop' om te stoppen):\n")

            # while True:
            #     user_question = question
            #     if user_question.lower() == 'stop':
            #         break

            #     response = chatbot_chain.invoke({"question": user_question})
            #     print(f"{selected_persona_data['naam']}: {response.content}\n")

            # print("Chatbot sessie beëindigd.")
        if not ps_response.content:
            return "❌ Fout: Geen antwoord ontvangen van de chatbot."
        else:
            return ps_response.content