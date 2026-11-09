# Prince-AI-Medical-Study-Assistant-
An offline-friendly AI Medical Study Assistant built with Python, featuring MCQs, flashcards, medical glossary, study notes, PDF reader, and progress tracking.


PROJECT: AI Medical Study Assistant & Clinical Suite
AUTHOR:  [PRINCE]
LICENSE: MIT License (GitHub Ready)
DESCRIPTION:
    A comprehensive, all-in-one desktop medical education platform built with
    Python, Tkinter, and SQLite3. Features an AI Clinical Study Assistant,
    Anatomy & Physiology Glossary, USMLE-style MCQ Simulator, Active Recall
    Flashcards, Clinical Notes Manager, Study Planner, Textbook PDF Reader,
    and a real-time Visual Progress Dashboard.
================================================================================
"""

import os
import sys
import json
import time
import random
import sqlite3
import datetime
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

# Optional PDF dependency handling for GitHub portability
try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# ==============================================================================
# 1. GLOBAL BRANDING & CONFIGURATION (CUSTOMIZE YOUR NAME HERE)
# ==============================================================================
PRINCE = "Prince"
AUTHOR_NAME = "PRINCE"
APP_TITLE = f"{PRINCE}'s AI Medical Study Assistant"
APP_VERSION = "2.4.0-Pro"
DB_FILENAME = f"{PRINCE.lower().replace(' ', '_').replace('.', '')}_med_assistant.db"

# Color Palette - Modern Medical Dark/Slate Theme
THEME = {
    "bg_dark": "#0f172a",       # Deep Slate Blue
    "bg_panel": "#1e293b",      # Panel Background
    "bg_card": "#334155",       # Card Background
    "fg_primary": "#f8fafc",    # Crisp White
    "fg_secondary": "#94a3b8",  # Muted Silver
    "accent_blue": "#38bdf8",   # Medical Cyan/Blue
    "accent_green": "#22c55e",  # Vital Green
    "accent_red": "#ef4444",    # Emergency Red
    "accent_amber": "#f59e0b",  # Warning Amber
    "accent_purple": "#a855f7", # Pharmacology Purple
    "font_main": ("Segoe UI", 10),
    "font_bold": ("Segoe UI", 10, "bold"),
    "font_title": ("Segoe UI", 16, "bold"),
    "font_sub": ("Segoe UI", 12, "bold"),
    "font_mono": ("Consolas", 10)
}


# ==============================================================================
# 2. DATABASE ENGINE & PRE-LOADED HIGH-YIELD MEDICAL SEED DATA
# ==============================================================================
class MedicalDatabase:
    """Manages SQLite3 persistence and seeds initial high-yield medical data."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._initialize_schema()
        self._seed_initial_data()

    def _initialize_schema(self):
        """Creates all required tables for the 8 modules."""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS glossary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL UNIQUE,
                system TEXT NOT NULL,
                definition TEXT NOT NULL,
                clinical_pearl TEXT
            );

            CREATE TABLE IF NOT EXISTS mcqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_opt TEXT NOT NULL,
                explanation TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS mcq_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                mastery_level INTEGER DEFAULT 0,
                last_reviewed TEXT
            );

            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS study_planner (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                subject TEXT NOT NULL,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            );

            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def _seed_initial_data(self):
        """Populates database with high-yield medical content if empty."""
        # 1. Seed Anatomy & Physiology Glossary
        self.cursor.execute("SELECT COUNT(*) FROM glossary")
        if self.cursor.fetchone()[0] == 0:
            glossary_seed = [
                ("Circle of Willis", "Neuroanatomy",
                 "Anastomotic arterial ring at the base of the brain formed by the internal carotid and vertebrobasilar systems.",
                 "Berry aneurysms most commonly occur at the Anterior Communicating Artery (AComA), causing bitemporal hemianopsia or subarachnoid hemorrhage."),
                ("Frank-Starling Law", "Cardiovascular Physiology",
                 "The stroke volume of the left ventricle increases in response to an increase in end-diastolic volume (preload), up to a physiological limit.",
                 "Fails in decompensated heart failure where sarcomeres are stretched beyond optimal actin-myosin overlap."),
                ("Loop of Henle (Thick Ascending)", "Renal Physiology",
                 "Impermeable to water; actively reabsorbs Na+, K+, and 2Cl- via the NKCC2 cotransporter. Known as the diluting segment of the nephron.",
                 "Target site of Loop Diuretics (Furosemide, Bumetanide), which abolish the corticomedullary osmotic gradient and increase Ca2+ excretion."),
                ("Triangle of Calot", "Hepatobiliary Anatomy",
                 "Anatomical space bounded by the cystic duct (inferiorly), common hepatic duct (medially), and inferior surface of the liver (superiorly).",
                 "Contains the Cystic Artery and Lund's Node; critical landmark during laparoscopic cholecystectomy to avoid bile duct injury."),
                ("Bohr Effect", "Respiratory Physiology",
                 "Rightward shift of the oxygen-hemoglobin dissociation curve caused by increased H+ (low pH), elevated pCO2, increased 2,3-BPG, and hyperthermia.",
                 "Mnemonic: 'CADET, face Right!' (CO2, Acid, 2,3-DPG, Exercise, Temperature) facilitates O2 unloading at metabolically active tissues."),
                ("Peyer's Patches", "GI / Immunology",
                 "Aggregated lymphoid nodules found primarily in the lamina propria and submucosa of the ileum.",
                 "M-cells sample luminal antigens; hypertrophy in children after viral illness can act as a lead point for intussusception."),
                ("Renin-Angiotensin-Aldosterone System", "Endocrine / Renal",
                 "Hormonal cascade initiated by juxtaglomerular cells in response to low renal perfusion, sympathetic beta-1 activation, or low NaCl at macula densa.",
                 "Angiotensin II preferentially constricts the efferent arteriole via AT1 receptors to preserve GFR during renal hypoperfusion.")
            ]
            self.cursor.executemany(
                "INSERT INTO glossary (term, system, definition, clinical_pearl) VALUES (?, ?, ?, ?)",
                glossary_seed
            )

        # 2. Seed USMLE-Style MCQs
        self.cursor.execute("SELECT COUNT(*) FROM mcqs")
        if self.cursor.fetchone()[0] == 0:
            mcq_seed = [
                ("Cardiology",
                 "A 64-year-old man presents with crushing substernal chest pain radiating to his jaw. ECG shows ST-segment elevation in leads II, III, and aVF, accompanied by sinus bradycardia. Occlusion of which coronary artery is most likely responsible?",
                 "Left Anterior Descending (LAD) Artery",
                 "Left Circumflex (LCx) Artery",
                 "Right Coronary Artery (RCA)",
                 "Left Main Coronary Artery",
                 "C",
                 "Leads II, III, and aVF reflect the inferior wall of the left ventricle. In 85% of patients (right-dominant circulation), the Posterior Descending Artery (PDA) arises from the RCA, which also supplies the SA and AV nodes, explaining the sinus bradycardia."),
                ("Neurology",
                 "A 28-year-old woman presents with diplopia that worsens at the end of the day and difficulty chewing tough meat. Deep tendon reflexes and pupillary light reflexes are normal. Antibodies against which structure are most likely present?",
                 "Presynaptic voltage-gated calcium channels",
                 "Postsynaptic nicotinic acetylcholine receptors",
                 "Peripheral myelin P0 protein",
                 "Aquaporin-4 water channels",
                 "B",
                 "Myasthenia Gravis is caused by autoantibodies against postsynaptic nicotinic ACh receptors at the neuromuscular junction, presenting with fatigable ptosis, diplopia, and bulbar weakness that worsens with repetitive use."),
                ("Pharmacology",
                 "A patient treated for tuberculosis develops orange-red discoloration of urine and tears, and her oral contraceptive becomes ineffective. What is the mechanism of action of the offending drug?",
                 "Inhibition of mycolic acid synthesis",
                 "Inhibition of DNA-dependent RNA polymerase",
                 "Inhibition of arabinosyltransferase",
                 "Disruption of bacterial membrane potential",
                 "B",
                 "Rifampin inhibits bacterial DNA-dependent RNA polymerase (encoded by rpoB). It causes benign red-orange body fluids and is a potent CYP450 inducer, accelerating metabolism of oral contraceptives and warfarin."),
                ("Nephrology",
                 "A 9-year-old boy develops cola-colored urine and periorbital edema 2 weeks after recovering from a sore throat. Renal biopsy under electron microscopy will most likely reveal:",
                 "Effacement of podocyte foot processes",
                 "Linear IgG deposition along the glomerular basement membrane",
                 "Subepithelial immune complex 'humps'",
                 "Splitting of the lamina densa ('basket-weave' appearance)",
                 "C",
                 "Post-streptococcal glomerulonephritis (PSGN) is a Type III hypersensitivity reaction characterized by lumpy-bumpy immunofluorescent staining and subepithelial dense immune complex 'humps' on electron microscopy."),
                ("Pathology",
                 "A 55-year-old man with chronic gastroesophageal reflux disease (GERD) undergoes upper endoscopy. Biopsy of the distal esophagus shows columnar epithelium with goblet cells. This cellular adaptation is an example of:",
                 "Dysplasia",
                 "Hypertrophy",
                 "Hyperplasia",
                 "Metaplasia",
                 "D",
                 "Barrett esophagus represents intestinal metaplasia: the reversible replacement of non-keratinized stratified squamous epithelium with mucin-producing simple columnar epithelium containing goblet cells in response to chronic acid stress.")
            ]
            self.cursor.executemany(
                "INSERT INTO mcqs (subject, question, option_a, option_b, option_c, option_d, correct_opt, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                mcq_seed
            )

        # 3. Seed Flashcards
        self.cursor.execute("SELECT COUNT(*) FROM flashcards")
        if self.cursor.fetchone()[0] == 0:
            flashcards_seed = [
                ("Cranial Nerves", "What structures pass through the Jugular Foramen?",
                 "Cranial Nerves IX (Glossopharyngeal), X (Vagus), XI (Accessory), and the Internal Jugular Vein (Sigmoid Sinus continuation).", 1),
                ("Cardiology", "What is Beck's Triad for Cardiac Tamponade?",
                 "1. Hypotension\n2. Jugular Venous Distension (JVD)\n3. Muffled/Distant Heart Sounds", 2),
                ("Pharmacology", "Antidote for Acetaminophen (Paracetamol) Overdose?",
                 "N-Acetylcysteine (NAC) — replenishes hepatic glutathione stores to detoxify NAPQI.", 3),
                ("Microbiology", "Virulence factors of Bacillus anthracis?",
                 "1. Poly-D-glutamate capsule (antiphagocytic)\n2. Edema Toxin (adenylate cyclase -> increases cAMP)\n3. Lethal Toxin (metalloprotease -> cleaves MAPKK)", 1),
                ("Endocrinology", "MEN 2A vs MEN 2B (RET proto-oncogene)?",
                 "MEN 2A: Medullary Thyroid Ca, Pheochromocytoma, Parathyroid Hyperplasia.\nMEN 2B: Medullary Thyroid Ca, Pheochromocytoma, Mucosal Neuromas + Marfanoid habitus.", 0)
            ]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d")
            for deck, front, back, mastery in flashcards_seed:
                self.cursor.execute(
                    "INSERT INTO flashcards (deck, front, back, mastery_level, last_reviewed) VALUES (?, ?, ?, ?, ?)",
                    (deck, front, back, mastery, now_str)
                )

        # 4. Seed Study Notes
        self.cursor.execute("SELECT COUNT(*) FROM study_notes")
        if self.cursor.fetchone()[0] == 0:
            notes_seed = [
                ("Heart Murmurs High-Yield Summary", "Cardiology",
                 "SYSTOLIC MURMURS:\n"
                 "• Aortic Stenosis: Crescendo-decrescendo systolic ejection murmur at right 2nd ICS, radiates to carotids. Pulsus parvus et tardus.\n"
                 "• Mitral Regurgitation: Holosystolic blowing murmur at apex, radiates to axilla.\n"
                 "• MVP: Mid-systolic click followed by late systolic murmur.\n\n"
                 "DIASTOLIC MURMURS:\n"
                 "• Aortic Regurgitation: Early decrescendo diastolic murmur at left sternal border; wide pulse pressure, water-hammer pulse.\n"
                 "• Mitral Stenosis: Opening snap followed by delayed rumbling diastolic murmur at apex. Most commonly secondary to Rheumatic Fever.",
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
                ("Acid-Base Disorders & Winter's Formula", "Nephrology",
                 "1. Check pH (<7.35 Acidemia, >7.45 Alkalemia)\n"
                 "2. Check HCO3- and pCO2\n"
                 "3. Calculate Anion Gap: AG = Na+ - (Cl- + HCO3-) [Normal: 8-12 mEq/L]\n"
                 "4. MUDPILES Mnemonic for High AG Metabolic Acidosis:\n"
                 "   Methanol, Uremia, DKA, Propylene glycol, Isoniazid/Iron, Lactic acidosis, Ethylene glycol, Salicylates.\n"
                 "5. Winter's Formula (Respiratory Compensation): Expected pCO2 = 1.5(HCO3-) + 8 ± 2",
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            ]
            self.cursor.executemany(
                "INSERT INTO study_notes (title, category, content, updated_at) VALUES (?, ?, ?, ?)",
                notes_seed
            )

        # 5. Seed Study Planner
        self.cursor.execute("SELECT COUNT(*) FROM study_planner")
        if self.cursor.fetchone()[0] == 0:
            planner_seed = [
                ("Complete 40 Cardiology MCQ Block", "Cardiology", "2026-11-10", "High", "Pending"),
                ("Review Brachial Plexus Lesions & Myotomes", "Anatomy", "2026-11-12", "High", "Pending"),
                ("Memorize Autonomic Pharmacology Cholinomimetics", "Pharmacology", "2026-11-15", "Medium", "Completed"),
                ("Read Robbins Pathology Chapter 3: Inflammation", "Pathology", "2026-11-18", "Low", "Pending")
            ]
            self.cursor.executemany(
                "INSERT INTO study_planner (task, subject, due_date, priority, status) VALUES (?, ?, ?, ?, ?)",
                planner_seed
            )

        self.conn.commit()


# ==============================================================================
# 3. AI CLINICAL STUDY ASSISTANT ENGINE (OFFLINE + API HYBRID)
# ==============================================================================
class AIMedicalEngine:
    """
    Provides instant clinical reasoning, mnemonics, differential diagnosis,
    and study synthesis. Searches local database + built-in clinical knowledge
    graph, and supports optional OpenAI/Compatible REST API keys.
    """

    KNOWLEDGE_GRAPH = {
        "shock": (
            "**Clinical Classification of Shock:**\n"
            "1. **Hypovolemic:** ↓ Preload (CVP), ↓ CO, ↑ SVR. (Hemorrhage, Dehydration)\n"
            "2. **Cardiogenic:** ↑ Preload (CVP/PCWP), ↓ CO, ↑ SVR. (Massive MI, Tamponade)\n"
            "3. **Distributive (Septic/Anaphylactic):** ↓ Preload, ↑ CO (early warm shock), ↓↓ SVR.\n"
            "4. **Neurogenic:** ↓ Preload, ↓ CO, ↓ SVR with **Bradycardia** (loss of sympathetic tone)."
        ),
        "cranial nerve": (
            "**High-Yield Cranial Nerve Reflexes (Afferent -> Efferent):**\n"
            "• **Pupillary Light Reflex:** CN II -> CN III\n"
            "• **Corneal (Blink) Reflex:** CN V1 -> CN VII (bilateral)\n"
            "• **Jaw Jerk Reflex:** CN V3 -> CN V3\n"
            "• **Gag Reflex:** CN IX -> CN X\n"
            "• **Vestibulo-Ocular Reflex:** CN VIII -> CN III, IV, VI"
        ),
        "antibiotic": (
            "**High-Yield Antibiotic Mechanisms:**\n"
            "• **30S Inhibitors ('Buy AT 30'):** Aminoglycosides (bactericidal), Tetracyclines (bacteriostatic).\n"
            "• **50S Inhibitors ('CCEL at 50'):** Chloramphenicol, Clindamycin, Erythromycin (Macrolides), Linezolid.\n"
            "• **Cell Wall Synthesis:** Penicillins, Cephalosporins, Carbapenems, Vancomycin (binds D-Ala-D-Ala)."
        ),
        "ecg": (
            "**Coronary Artery Territory Localization on ECG:**\n"
            "• **V1–V2:** Anteroseptal -> Left Anterior Descending (LAD)\n"
            "• **V3–V4:** Anteroapical -> Distal LAD\n"
            "• **I, aVL, V5–V6:** Lateral -> Left Circumflex (LCx)\n"
            "• **II, III, aVF:** Inferior -> Right Coronary Artery (RCA)"
        ),
        "diabetes": (
            "**DKA vs. HHS Clinical Differentiation:**\n"
            "• **DKA (Type 1 DM):** Acute onset, Kussmaul respirations, fruity odor, Glucose 250–600 mg/dL, High Anion Gap Acidosis, Serum Ketones +++.\n"
            "• **HHS (Type 2 DM):** Insidious onset, profound dehydration + focal neuro deficits, Glucose >600 mg/dL, Normal pH (>7.30), minimal ketosis."
        )
    }

    def __init__(self, db: MedicalDatabase):
        self.db = db
        self.api_key = os.environ.get("OPENAI_API_KEY", "")

    def generate_response(self, query: str) -> str:
        q_clean = query.strip().lower()
        if not q_clean:
            return "Please enter a medical topic, clinical vignette, or anatomy question."

        # 1. Check if user is asking for a quiz or flashcard summary
        if "quiz me" in q_clean or "give me a question" in q_clean:
            self.db.cursor.execute("SELECT subject, question, correct_opt, explanation FROM mcqs ORDER BY RANDOM() LIMIT 1")
            row = self.db.cursor.fetchone()
            if row:
                return (f"**Quick Clinical Vignette ({row['subject']}):**\n"
                        f"{row['question']}\n\n"
                        f"*(Tip: Head over to the MCQ Practice tab to test yourself interactively! Correct Answer: {row['correct_opt']})*")

        # 2. Search Local Glossary Database for matching terms
        self.db.cursor.execute(
            "SELECT term, system, definition, clinical_pearl FROM glossary WHERE LOWER(term) LIKE ? OR LOWER(definition) LIKE ?",
            (f"%{q_clean}%", f"%{q_clean}%")
        )
        glossary_matches = self.db.cursor.fetchall()
        if glossary_matches:
            out = [f"### Clinical Database Match Found by {AUTHOR_NAME}'s AI:"]
            for m in glossary_matches[:2]:
                out.append(f"• **{m['term']}** ({m['system']}): {m['definition']}\n  *Clinical Pearl:* {m['clinical_pearl']}")
            return "\n\n".join(out)

        # 3. Search Local Notes
        self.db.cursor.execute(
            "SELECT title, category, content FROM study_notes WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
            (f"%{q_clean}%", f"%{q_clean}%")
        )
        note_matches = self.db.cursor.fetchall()
        if note_matches:
            n = note_matches[0]
            return f"**From Your '{n['category']}' Study Notes ({n['title']}):**\n\n{n['content']}"

        # 4. Search Built-in Knowledge Graph
        for key, text in self.KNOWLEDGE_GRAPH.items():
            if key in q_clean:
                return text

        # 5. Optional Live Cloud LLM Query if API Key is configured
        if self.api_key:
            try:
                req_data = json.dumps({
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": f"You are {AUTHOR_NAME}'s AI Medical Study Assistant. Provide concise, high-yield USMLE/Medical board explanations with clinical pearls."},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.openai.com/v1/chat/completions",
                    data=req_data,
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    return res_json["choices"][0]["message"]["content"]
            except Exception as e:
                return f"[Cloud API Error: {e}]\nFalling back to local clinical framework..."

        # 6. Structured Clinical Reasoning Framework Fallback
        return (
            f"**{AUTHOR_NAME}'s AI Clinical Framework for '{query.title()}':**\n"
            f"1. **Pathophysiology:** Consider cellular adaptation, receptor signaling, or anatomical borders involved in *{query}*.\n"
            f"2. **Clinical Presentation:** Identify classic triad, chief complaint, and physical exam maneuvers.\n"
            f"3. **Diagnostic Workup:** First-line screening test vs. Gold-standard confirmatory assay.\n"
            f"4. **Management:** Acute stabilization (ABCs) followed by targeted pharmacotherapy.\n\n"
            f"*Tip: Try asking about 'Shock', 'ECG', 'Cranial Nerves', 'Antibiotics', 'Diabetes', 'Circle of Willis', 'Frank-Starling', or click 'Set API Key' for live LLM generation.*"
        )


# ==============================================================================
# 4. MAIN DESKTOP APPLICATION GUI (TKINTER)
# ==============================================================================
class MedicalStudyAssistantApp(tk.Tk):
    """Main Tkinter Application Window orchestrating all 8 medical study modules."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} — v{APP_VERSION}")
        self.geometry("1280x820")
        self.minsize(1080, 720)
        self.configure(bg=THEME["bg_dark"])

        # Initialize Database & AI Engine
        self.db = MedicalDatabase(DB_FILENAME)
        self.ai_engine = AIMedicalEngine(self.db)

        # Configure TTK Styles
        self._setup_styles()

        # Layout Containers
        self._build_header()
        self._build_main_workspace()

        # Active Module Reference
        self.current_module_frame = None
        self.show_module("dashboard")

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background=THEME["bg_panel"],
                        foreground=THEME["fg_primary"],
                        fieldbackground=THEME["bg_panel"],
                        rowheight=28,
                        font=THEME["font_main"])
        style.configure("Treeview.Heading",
                        background=THEME["bg_card"],
                        foreground=THEME["accent_blue"],
                        font=THEME["font_bold"])
        style.map("Treeview", background=[("selected", THEME["accent_blue"])],
                  foreground=[("selected", THEME["bg_dark"])])

    def _build_header(self):
        header = tk.Frame(self, bg=THEME["bg_panel"], height=64, padx=20, pady=10)
        header.pack(side=tk.TOP, fill=tk.X)

        title_lbl = tk.Label(
            header,
            text=f"🩺 {APP_TITLE}",
            bg=THEME["bg_panel"],
            fg=THEME["accent_blue"],
            font=THEME["font_title"]
        )
        title_lbl.pack(side=tk.LEFT)

        badge_lbl = tk.Label(
            header,
            text=f"GitHub Edition • Curated by {AUTHOR_NAME}",
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
            font=THEME["font_bold"],
            padx=12,
            pady=4
        )
        badge_lbl.pack(side=tk.RIGHT)

    def _build_main_workspace(self):
        workspace = tk.Frame(self, bg=THEME["bg_dark"])
        workspace.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Navigation Sidebar
        self.sidebar = tk.Frame(workspace, bg=THEME["bg_panel"], width=240, padx=10, pady=15)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        nav_items = [
            ("📊  Progress Dashboard", "dashboard"),
            ("🤖  AI Study Assistant", "ai_assistant"),
            ("🧬  Anatomy & Physiology", "glossary"),
            ("📝  MCQ Practice System", "mcq"),
            ("🗂️  Flashcard Generator", "flashcards"),
            ("📓  Clinical Study Notes", "notes"),
            ("📅  Study Planner", "planner"),
            ("📄  Medical PDF Reader", "pdf_reader")
        ]

        self.nav_buttons = {}
        for label, key in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label,
                anchor="w",
                bg=THEME["bg_panel"],
                fg=THEME["fg_primary"],
                activebackground=THEME["accent_blue"],
                activeforeground=THEME["bg_dark"],
                font=THEME["font_bold"],
                bd=0,
                padx=14,
                pady=11,
                cursor="hand2",
                command=lambda k=key: self.show_module(k)
            )
            btn.pack(fill=tk.X, pady=3)
            self.nav_buttons[key] = btn

        # Footer Info in Sidebar
        footer_lbl = tk.Label(
            self.sidebar,
            text=f"DB: {DB_FILENAME}\nStatus: Online (SQLite3)",
            bg=THEME["bg_panel"],
            fg=THEME["fg_secondary"],
            font=("Segoe UI", 8),
            justify=tk.LEFT
        )
        footer_lbl.pack(side=tk.BOTTOM, anchor="w", pady=5)

        # Right Dynamic Content Area
        self.content_area = tk.Frame(workspace, bg=THEME["bg_dark"], padx=20, pady=20)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_module(self, module_key: str):
        """Switches between the 8 medical modules seamlessly."""
        for k, btn in self.nav_buttons.items():
            if k == module_key:
                btn.configure(bg=THEME["accent_blue"], fg=THEME["bg_dark"])
            else:
                btn.configure(bg=THEME["bg_panel"], fg=THEME["fg_primary"])

        if self.current_module_frame is not None:
            self.current_module_frame.destroy()

        self.current_module_frame = tk.Frame(self.content_area, bg=THEME["bg_dark"])
        self.current_module_frame.pack(fill=tk.BOTH, expand=True)

        builders = {
            "dashboard": self._build_dashboard_module,
            "ai_assistant": self._build_ai_module,
            "glossary": self._build_glossary_module,
            "mcq": self._build_mcq_module,
            "flashcards": self._build_flashcards_module,
            "notes": self._build_notes_module,
            "planner": self._build_planner_module,
            "pdf_reader": self._build_pdf_module
        }
        builders[module_key](self.current_module_frame)

    # ==========================================================================
    # MODULE 1: PROGRESS DASHBOARD (ANALYTICS & VISUAL CHARTS)
    # ==========================================================================
    def _build_dashboard_module(self, parent: tk.Frame):
        tk.Label(parent, text=f"Welcome back, {AUTHOR_NAME}! Clinical Readiness Overview",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(anchor="w", pady=(0, 15))

        # Fetch live metrics from SQLite
        c = self.db.cursor
        c.execute("SELECT COUNT(*) FROM glossary")
        total_terms = c.fetchone()[0]

        c.execute("SELECT COUNT(*), SUM(is_correct) FROM mcq_history")
        mcq_row = c.fetchone()
        total_attempts = mcq_row[0] or 0
        correct_attempts = mcq_row[1] or 0
        accuracy = round((correct_attempts / total_attempts) * 100, 1) if total_attempts > 0 else 0.0

        c.execute("SELECT COUNT(*) FROM flashcards WHERE mastery_level >= 2")
        mastered_cards = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM flashcards")
        total_cards = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM study_planner WHERE status = 'Completed'")
        done_tasks = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM study_planner")
        all_tasks = c.fetchone()[0]

        # Top KPI Cards Row
        kpi_frame = tk.Frame(parent, bg=THEME["bg_dark"])
        kpi_frame.pack(fill=tk.X, pady=(0, 20))

        kpis = [
            ("MCQ Accuracy Rate", f"{accuracy}% ({correct_attempts}/{total_attempts})", THEME["accent_green"]),
            ("Flashcards Mastered", f"{mastered_cards} / {total_cards} Cards", THEME["accent_blue"]),
            ("A&P Glossary Bank", f"{total_terms} High-Yield Terms", THEME["accent_purple"]),
            ("Study Tasks Completed", f"{done_tasks} / {all_tasks} Tasks", THEME["accent_amber"])
        ]

        for idx, (label, val, color) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=THEME["bg_panel"], padx=18, pady=16, highlightthickness=1, highlightbackground=color)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if idx == 0 else 10, 0))
            tk.Label(card, text=label, bg=THEME["bg_panel"], fg=THEME["fg_secondary"], font=THEME["font_bold"]).pack(anchor="w")
            tk.Label(card, text=val, bg=THEME["bg_panel"], fg=color, font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(6, 0))

        # Visual Bar Chart Canvas for Subject Performance
        chart_panel = tk.Frame(parent, bg=THEME["bg_panel"], padx=20, pady=15)
        chart_panel.pack(fill=tk.BOTH, expand=True)

        tk.Label(chart_panel, text="Subject Mastery & Question Bank Distribution",
                 bg=THEME["bg_panel"], fg=THEME["fg_primary"], font=THEME["font_sub"]).pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(chart_panel, bg=THEME["bg_dark"], height=320, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Aggregate counts per subject across MCQs and Notes
        subjects = ["Cardiology", "Neurology", "Pharmacology", "Nephrology", "Pathology", "Anatomy"]
        bar_colors = [THEME["accent_red"], THEME["accent_blue"], THEME["accent_purple"],
                      THEME["accent_green"], THEME["accent_amber"], "#ec4899"]

        x_start = 70
        bar_width = 75
        spacing = 60
        max_bar_h = 210
        base_y = 265

        for i, subj in enumerate(subjects):
            c.execute("SELECT COUNT(*) FROM mcqs WHERE LOWER(subject) LIKE ?", (f"%{subj.lower()}%",))
            m_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM study_planner WHERE LOWER(subject) LIKE ?", (f"%{subj.lower()}%",))
            p_count = c.fetchone()[0]
            score_val = min(100, (m_count * 25) + (p_count * 20) + 30)

            bar_h = int((score_val / 100.0) * max_bar_h)
            x0 = x_start + i * (bar_width + spacing)
            y0 = base_y - bar_h
            x1 = x0 + bar_width
            y1 = base_y

            canvas.create_rectangle(x0, y0, x1, y1, fill=bar_colors[i % len(bar_colors)], outline="")
            canvas.create_text((x0 + x1) / 2, y0 - 15, text=f"{score_val}%", fill=THEME["fg_primary"], font=THEME["font_bold"])
            canvas.create_text((x0 + x1) / 2, base_y + 20, text=subj, fill=THEME["fg_secondary"], font=THEME["font_bold"])

    # ==========================================================================
    # MODULE 2: AI MEDICAL STUDY ASSISTANT
    # ==========================================================================
    def _build_ai_module(self, parent: tk.Frame):
        top_bar = tk.Frame(parent, bg=THEME["bg_dark"])
        top_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_bar, text=f"🤖 {AUTHOR_NAME}'s AI Clinical Tutor",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(side=tk.LEFT)

        tk.Button(top_bar, text="🔑 Set OpenAI API Key (Optional)", bg=THEME["bg_card"], fg=THEME["accent_blue"],
                  font=THEME["font_bold"], bd=0, padx=12, pady=6,
                  command=self._prompt_api_key).pack(side=tk.RIGHT)

        # Chat History ScrolledText
        self.chat_display = scrolledtext.ScrolledText(
            parent, bg=THEME["bg_panel"], fg=THEME["fg_primary"],
            font=THEME["font_main"], wrap=tk.WORD, padx=15, pady=15, bd=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.chat_display.insert(
            tk.END,
            f"🩺 Welcome to {AUTHOR_NAME}'s AI Medical Study Assistant!\n"
            f"Ask me about Anatomy, Physiology, Pathology, Pharmacology, ECG localization, Shock, Cranial Nerves, or type 'Quiz me'!\n"
            f"{'-'*85}\n\n"
        )
        self.chat_display.configure(state=tk.DISABLED)

        # Quick Prompt Buttons
        quick_frame = tk.Frame(parent, bg=THEME["bg_dark"])
        quick_frame.pack(fill=tk.X, pady=(0, 8))
        for topic in ["Shock Classification", "Cranial Nerve Reflexes", "ECG Territories", "DKA vs HHS", "Circle of Willis", "Quiz Me"]:
            tk.Button(
                quick_frame, text=topic, bg=THEME["bg_card"], fg=THEME["fg_secondary"],
                font=("Segoe UI", 9), bd=0, padx=10, pady=4,
                command=lambda t=topic: self._send_ai_prompt(t)
            ).pack(side=tk.LEFT, padx=(0, 6))

        # Input Row
        input_row = tk.Frame(parent, bg=THEME["bg_dark"])
        input_row.pack(fill=tk.X)

        self.ai_entry = tk.Entry(
            input_row, bg=THEME["bg_panel"], fg=THEME["fg_primary"],
            insertbackground=THEME["fg_primary"], font=("Segoe UI", 11), bd=0
        )
        self.ai_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=10, padx=(0, 10))
        self.ai_entry.bind("<Return>", lambda e: self._send_ai_prompt())

        tk.Button(
            input_row, text="Ask AI Tutor ➤", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
            font=THEME["font_bold"], bd=0, padx=20, pady=10,
            command=self._send_ai_prompt
        ).pack(side=tk.RIGHT)

    def _send_ai_prompt(self, preset_text: str = None):
        user_text = preset_text if preset_text else self.ai_entry.get().strip()
        if not user_text:
            return
        if not preset_text:
            self.ai_entry.delete(0, tk.END)

        reply = self.ai_engine.generate_response(user_text)
        now_str = datetime.datetime.now().strftime("%H:%M")

        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{now_str}] 👤 {AUTHOR_NAME}: {user_text}\n\n")
        self.chat_display.insert(tk.END, f"[{now_str}] 🤖 AI Assistant:\n{reply}\n\n{'-'*85}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _prompt_api_key(self):
        win = tk.Toplevel(self)
        win.title("Configure Optional LLM API Key")
        win.geometry("420x160")
        win.configure(bg=THEME["bg_panel"])
        tk.Label(win, text="Enter OpenAI API Key (leave blank for Offline Clinical Engine):",
                 bg=THEME["bg_panel"], fg=THEME["fg_primary"], font=THEME["font_bold"]).pack(pady=12)
        key_entry = tk.Entry(win, width=45, show="*")
        key_entry.insert(0, self.ai_engine.api_key)
        key_entry.pack(pady=5)

        def save_key():
            self.ai_engine.api_key = key_entry.get().strip()
            messagebox.showinfo("Saved", "API Key updated successfully!")
            win.destroy()

        tk.Button(win, text="Save Key", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], command=save_key).pack(pady=12)

    # ==========================================================================
    # MODULE 3: ANATOMY & PHYSIOLOGY GLOSSARY
    # ==========================================================================
    def _build_glossary_module(self, parent: tk.Frame):
        tk.Label(parent, text="🧬 Anatomy & Physiology High-Yield Glossary",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(anchor="w", pady=(0, 12))

        # Search & Add Controls
        ctrl_row = tk.Frame(parent, bg=THEME["bg_dark"])
        ctrl_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(ctrl_row, text="Search Term/System:", bg=THEME["bg_dark"], fg=THEME["fg_secondary"],
                 font=THEME["font_bold"]).pack(side=tk.LEFT, padx=(0, 8))
        self.glossary_search_var = tk.StringVar()
        self.glossary_search_var.trace_add("write", lambda *args: self._refresh_glossary_list())
        tk.Entry(ctrl_row, textvariable=self.glossary_search_var, bg=THEME["bg_panel"],
                 fg=THEME["fg_primary"], insertbackground=THEME["fg_primary"], width=35).pack(side=tk.LEFT, ipady=5)

        tk.Button(ctrl_row, text="+ Add New Medical Term", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=14, pady=6,
                  command=self._add_glossary_dialog).pack(side=tk.RIGHT)

        # Split View: Treeview Left + Detail Card Right
        split = tk.Frame(parent, bg=THEME["bg_dark"])
        split.pack(fill=tk.BOTH, expand=True)

        cols = ("Term", "System")
        self.glossary_tree = ttk.Treeview(split, columns=cols, show="headings", width=38)
        self.glossary_tree.heading("Term", text="Anatomical / Physiological Term")
        self.glossary_tree.heading("System", text="Organ System")
        self.glossary_tree.column("Term", width=220)
        self.glossary_tree.column("System", width=160)
        self.glossary_tree.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.glossary_tree.bind("<<TreeviewSelect>>", self._on_glossary_select)

        # Detail Panel
        detail_card = tk.Frame(split, bg=THEME["bg_panel"], padx=20, pady=20)
        detail_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.g_title_lbl = tk.Label(detail_card, text="Select a term to view clinical details",
                                    bg=THEME["bg_panel"], fg=THEME["accent_blue"], font=THEME["font_title"], wraplength=500, justify=tk.LEFT)
        self.g_title_lbl.pack(anchor="w")

        self.g_sys_lbl = tk.Label(detail_card, text="", bg=THEME["bg_panel"], fg=THEME["accent_purple"], font=THEME["font_bold"])
        self.g_sys_lbl.pack(anchor="w", pady=(4, 15))

        self.g_def_text = scrolledtext.ScrolledText(detail_card, bg=THEME["bg_card"], fg=THEME["fg_primary"],
                                                    font=("Segoe UI", 11), wrap=tk.WORD, height=12, bd=0, padx=12, pady=12)
        self.g_def_text.pack(fill=tk.BOTH, expand=True)

        self._refresh_glossary_list()

    def _refresh_glossary_list(self):
        for item in self.glossary_tree.get_children():
            self.glossary_tree.delete(item)
        q = self.glossary_search_var.get().strip().lower()
        self.db.cursor.execute(
            "SELECT id, term, system FROM glossary WHERE LOWER(term) LIKE ? OR LOWER(system) LIKE ? ORDER BY term ASC",
            (f"%{q}%", f"%{q}%")
        )
        for row in self.db.cursor.fetchall():
            self.glossary_tree.insert("", tk.END, iid=str(row["id"]), values=(row["term"], row["system"]))

    def _on_glossary_select(self, event):
        sel = self.glossary_tree.selection()
        if not sel:
            return
        term_id = int(sel[0])
        self.db.cursor.execute("SELECT * FROM glossary WHERE id = ?", (term_id,))
        row = self.db.cursor.fetchone()
        if row:
            self.g_title_lbl.configure(text=row["term"])
            self.g_sys_lbl.configure(text=f"Organ System: {row['system']}")
            self.g_def_text.configure(state=tk.NORMAL)
            self.g_def_text.delete("1.0", tk.END)
            self.g_def_text.insert(tk.END, f"📘 DEFINITION:\n{row['definition']}\n\n⚡ HIGH-YIELD CLINICAL PEARL:\n{row['clinical_pearl']}")
            self.g_def_text.configure(state=tk.DISABLED)

    def _add_glossary_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add New Anatomy/Physiology Term")
        win.geometry("460x380")
        win.configure(bg=THEME["bg_panel"], padx=15, pady=15)

        fields = {}
        for lbl in ["Term Name", "Organ System", "Definition", "Clinical Pearl"]:
            tk.Label(win, text=lbl, bg=THEME["bg_panel"], fg=THEME["fg_primary"], font=THEME["font_bold"]).pack(anchor="w", pady=(6, 2))
            ent = tk.Entry(win, width=50)
            ent.pack(fill=tk.X, ipady=4)
            fields[lbl] = ent

        def save_term():
            t = fields["Term Name"].get().strip()
            s = fields["Organ System"].get().strip()
            d = fields["Definition"].get().strip()
            p = fields["Clinical Pearl"].get().strip()
            if not (t and s and d):
                messagebox.showwarning("Incomplete", "Term, System, and Definition are required.")
                return
            try:
                self.db.cursor.execute("INSERT INTO glossary (term, system, definition, clinical_pearl) VALUES (?, ?, ?, ?)", (t, s, d, p))
                self.db.conn.commit()
                self._refresh_glossary_list()
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate", "That medical term already exists in the glossary.")

        tk.Button(win, text="Save to Glossary", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], pady=8, command=save_term).pack(pady=15, fill=tk.X)

    # ==========================================================================
    # MODULE 4: USMLE-STYLE MCQ PRACTICE SYSTEM
    # ==========================================================================
    def _build_mcq_module(self, parent: tk.Frame):
        header_row = tk.Frame(parent, bg=THEME["bg_dark"])
        header_row.pack(fill=tk.X, pady=(0, 12))

        tk.Label(header_row, text="📝 Clinical Vignette MCQ Simulator",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(side=tk.LEFT)

        tk.Button(header_row, text="+ Create Custom MCQ", bg=THEME["bg_card"], fg=THEME["accent_blue"],
                  font=THEME["font_bold"], bd=0, padx=12, pady=6,
                  command=self._add_mcq_dialog).pack(side=tk.RIGHT)

        self.db.cursor.execute("SELECT * FROM mcqs")
        self.mcq_list = self.db.cursor.fetchall()
        self.mcq_idx = 0
        self.selected_mcq_opt = tk.StringVar(value="")

        self.mcq_card = tk.Frame(parent, bg=THEME["bg_panel"], padx=25, pady=20)
        self.mcq_card.pack(fill=tk.BOTH, expand=True)

        self.mcq_meta_lbl = tk.Label(self.mcq_card, text="", bg=THEME["bg_panel"], fg=THEME["accent_amber"], font=THEME["font_bold"])
        self.mcq_meta_lbl.pack(anchor="w")

        self.mcq_q_lbl = tk.Label(self.mcq_card, text="", bg=THEME["bg_panel"], fg=THEME["fg_primary"],
                                  font=("Segoe UI", 12), wraplength=920, justify=tk.LEFT)
        self.mcq_q_lbl.pack(anchor="w", pady=(10, 18))

        self.opt_buttons = {}
        for opt_code in ["A", "B", "C", "D"]:
            rb = tk.Radiobutton(
                self.mcq_card, text="", variable=self.selected_mcq_opt, value=opt_code,
                bg=THEME["bg_card"], fg=THEME["fg_primary"], selectcolor=THEME["bg_dark"],
                activebackground=THEME["bg_card"], activeforeground=THEME["accent_blue"],
                font=("Segoe UI", 11), anchor="w", padx=15, pady=8, indicatoron=True
            )
            rb.pack(fill=tk.X, pady=4)
            self.opt_buttons[opt_code] = rb

        btn_bar = tk.Frame(self.mcq_card, bg=THEME["bg_panel"])
        btn_bar.pack(fill=tk.X, pady=15)

        tk.Button(btn_bar, text="✔ Submit Answer", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=18, pady=8, command=self._submit_mcq).pack(side=tk.LEFT)

        tk.Button(btn_bar, text="Next Vignette ➔", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=18, pady=8, command=self._next_mcq).pack(side=tk.LEFT, padx=12)

        self.mcq_exp_box = scrolledtext.ScrolledText(self.mcq_card, bg=THEME["bg_dark"], fg=THEME["fg_secondary"],
                                                     font=THEME["font_main"], height=7, wrap=tk.WORD, bd=0, padx=12, pady=12)
        self.mcq_exp_box.pack(fill=tk.BOTH, expand=True)

        self._load_current_mcq()

    def _load_current_mcq(self):
        if not self.mcq_list:
            return
        q = self.mcq_list[self.mcq_idx % len(self.mcq_list)]
        self.selected_mcq_opt.set("")
        self.mcq_meta_lbl.configure(text=f"Question {(self.mcq_idx % len(self.mcq_list)) + 1} of {len(self.mcq_list)}  •  Subject: {q['subject']}")
        self.mcq_q_lbl.configure(text=q["question"])
        self.opt_buttons["A"].configure(text=f"A.  {q['option_a']}")
        self.opt_buttons["B"].configure(text=f"B.  {q['option_b']}")
        self.opt_buttons["C"].configure(text=f"C.  {q['option_c']}")
        self.opt_buttons["D"].configure(text=f"D.  {q['option_d']}")
        self.mcq_exp_box.configure(state=tk.NORMAL)
        self.mcq_exp_box.delete("1.0", tk.END)
        self.mcq_exp_box.insert(tk.END, "Select an option and click 'Submit Answer' to view the detailed pathophysiology rationale.")
        self.mcq_exp_box.configure(state=tk.DISABLED)

    def _submit_mcq(self):
        choice = self.selected_mcq_opt.get()
        if not choice:
            messagebox.showinfo("Select Option", "Please select an answer choice (A-D) first.")
            return
        q = self.mcq_list[self.mcq_idx % len(self.mcq_list)]
        is_corr = 1 if choice == q["correct_opt"] else 0
        self.db.cursor.execute(
            "INSERT INTO mcq_history (subject, is_correct, timestamp) VALUES (?, ?, ?)",
            (q["subject"], is_corr, datetime.datetime.now().isoformat())
        )
        self.db.conn.commit()

        verdict = "✅ CORRECT!" if is_corr else f"❌ INCORRECT (Correct Answer: {q['correct_opt']})"
        self.mcq_exp_box.configure(state=tk.NORMAL, fg=THEME["accent_green"] if is_corr else THEME["accent_red"])
        self.mcq_exp_box.delete("1.0", tk.END)
        self.mcq_exp_box.insert(tk.END, f"{verdict}\n\n📘 EDUCATIONAL OBJECTIVE & RATIONALE:\n{q['explanation']}")
        self.mcq_exp_box.configure(state=tk.DISABLED)

    def _next_mcq(self):
        self.mcq_idx += 1
        self._load_current_mcq()

    def _add_mcq_dialog(self):
        win = tk.Toplevel(self)
        win.title("Add Custom USMLE Question")
        win.geometry("500x520")
        win.configure(bg=THEME["bg_panel"], padx=15, pady=15)

        entries = {}
        for label in ["Subject", "Question Stem", "Option A", "Option B", "Option C", "Option D", "Correct (A/B/C/D)", "Explanation"]:
            tk.Label(win, text=label, bg=THEME["bg_panel"], fg=THEME["fg_primary"], font=THEME["font_bold"]).pack(anchor="w", pady=(4, 1))
            e = tk.Entry(win)
            e.pack(fill=tk.X, ipady=3)
            entries[label] = e

        def save():
            vals = [entries[k].get().strip() for k in entries]
            if not all(vals) or vals[6].upper() not in ("A", "B", "C", "D"):
                messagebox.showwarning("Invalid", "Fill all fields and ensure Correct Option is A, B, C, or D.")
                return
            self.db.cursor.execute(
                "INSERT INTO mcqs (subject, question, option_a, option_b, option_c, option_d, correct_opt, explanation) VALUES (?,?,?,?,?,?,?,?)",
                (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6].upper(), vals[7])
            )
            self.db.conn.commit()
            self.db.cursor.execute("SELECT * FROM mcqs")
            self.mcq_list = self.db.cursor.fetchall()
            self._load_current_mcq()
            win.destroy()

        tk.Button(win, text="Save Question", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], pady=8, command=save).pack(fill=tk.X, pady=12)

    # ==========================================================================
    # MODULE 5: ACTIVE RECALL FLASHCARD GENERATOR
    # ==========================================================================
    def _build_flashcards_module(self, parent: tk.Frame):
        top = tk.Frame(parent, bg=THEME["bg_dark"])
        top.pack(fill=tk.X, pady=(0, 12))

        tk.Label(top, text="🗂️ Spaced-Repetition Medical Flashcards",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(side=tk.LEFT)

        tk.Button(top, text="+ Create Flashcard", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=14, pady=6, command=self._add_flashcard_dialog).pack(side=tk.RIGHT)

        self.db.cursor.execute("SELECT * FROM flashcards")
        self.cards_data = self.db.cursor.fetchall()
        self.card_idx = 0
        self.is_card_flipped = False

        # Interactive Card Canvas Frame
        self.card_box = tk.Frame(parent, bg=THEME["bg_panel"], padx=40, pady=40, highlightthickness=2, highlightbackground=THEME["accent_blue"])
        self.card_box.pack(fill=tk.BOTH, expand=True, pady=10)

        self.fc_deck_lbl = tk.Label(self.card_box, text="", bg=THEME["bg_panel"], fg=THEME["accent_purple"], font=THEME["font_sub"])
        self.fc_deck_lbl.pack(anchor="n")

        self.fc_content_lbl = tk.Label(
            self.card_box, text="", bg=THEME["bg_panel"], fg=THEME["fg_primary"],
            font=("Segoe UI", 16, "bold"), wraplength=820, justify=tk.CENTER
        )
        self.fc_content_lbl.pack(expand=True)

        # Controls Row
        ctrl = tk.Frame(parent, bg=THEME["bg_dark"])
        ctrl.pack(fill=tk.X, pady=10)

        tk.Button(ctrl, text="🔄 Flip Card (Front / Back)", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=24, pady=10, command=self._flip_flashcard).pack(side=tk.LEFT)

        tk.Button(ctrl, text="Again (Hard)", bg=THEME["accent_red"], fg=THEME["fg_primary"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=10,
                  command=lambda: self._rate_flashcard(0)).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(ctrl, text="Good", bg=THEME["accent_amber"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=10,
                  command=lambda: self._rate_flashcard(1)).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(ctrl, text="Easy (Mastered)", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=10,
                  command=lambda: self._rate_flashcard(2)).pack(side=tk.RIGHT)

        self._render_flashcard()

    def _render_flashcard(self):
        if not self.cards_data:
            return
        card = self.cards_data[self.card_idx % len(self.cards_data)]
        side_tag = "BACK (ANSWER)" if self.is_card_flipped else "FRONT (PROMPT)"
        self.fc_deck_lbl.configure(
            text=f"Deck: {card['deck']}  •  Card {(self.card_idx % len(self.cards_data)) + 1}/{len(self.cards_data)}  •  [{side_tag}]"
        )
        text_body = card["back"] if self.is_card_flipped else card["front"]
        self.fc_content_lbl.configure(
            text=text_body,
            fg=THEME["accent_green"] if self.is_card_flipped else THEME["fg_primary"]
        )

    def _flip_flashcard(self):
        self.is_card_flipped = not self.is_card_flipped
        self._render_flashcard()

    def _rate_flashcard(self, mastery_val: int):
        if not self.cards_data:
            return
        card = self.cards_data[self.card_idx % len(self.cards_data)]
        self.db.cursor.execute(
            "UPDATE flashcards SET mastery_level = ?, last_reviewed = ? WHERE id = ?",
            (mastery_val, datetime.datetime.now().strftime("%Y-%m-%d"), card["id"])
        )
        self.db.conn.commit()
        self.is_card_flipped = False
        self.card_idx += 1
        self.db.cursor.execute("SELECT * FROM flashcards")
        self.cards_data = self.db.cursor.fetchall()
        self._render_flashcard()

    def _add_flashcard_dialog(self):
        win = tk.Toplevel(self)
        win.title("Create New Flashcard")
        win.geometry("420x300")
        win.configure(bg=THEME["bg_panel"], padx=15, pady=15)

        tk.Label(win, text="Deck / Subject:", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(anchor="w")
        d_ent = tk.Entry(win)
        d_ent.pack(fill=tk.X, pady=4)

        tk.Label(win, text="Front (Question/Prompt):", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(anchor="w")
        f_ent = tk.Entry(win)
        f_ent.pack(fill=tk.X, pady=4)

        tk.Label(win, text="Back (High-Yield Answer):", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(anchor="w")
        b_ent = tk.Entry(win)
        b_ent.pack(fill=tk.X, pady=4)

        def save():
            if not (d_ent.get().strip() and f_ent.get().strip() and b_ent.get().strip()):
                return
            self.db.cursor.execute(
                "INSERT INTO flashcards (deck, front, back, mastery_level, last_reviewed) VALUES (?, ?, ?, 0, ?)",
                (d_ent.get().strip(), f_ent.get().strip(), b_ent.get().strip(), datetime.datetime.now().strftime("%Y-%m-%d"))
            )
            self.db.conn.commit()
            self.db.cursor.execute("SELECT * FROM flashcards")
            self.cards_data = self.db.cursor.fetchall()
            self._render_flashcard()
            win.destroy()

        tk.Button(win, text="Add Card", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], pady=8, command=save).pack(fill=tk.X, pady=15)

    # ==========================================================================
    # MODULE 6: CLINICAL STUDY NOTES MANAGER
    # ==========================================================================
    def _build_notes_module(self, parent: tk.Frame):
        tk.Label(parent, text="📓 Clinical Study Notes & Summaries",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(anchor="w", pady=(0, 12))

        split = tk.Frame(parent, bg=THEME["bg_dark"])
        split.pack(fill=tk.BOTH, expand=True)

        # Left Note List
        left_col = tk.Frame(split, bg=THEME["bg_panel"], width=280, padx=10, pady=10)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        tk.Button(left_col, text="+ New Clinical Note", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, pady=8, command=self._new_note_clear).pack(fill=tk.X, pady=(0, 10))

        self.notes_listbox = tk.Listbox(left_col, bg=THEME["bg_card"], fg=THEME["fg_primary"],
                                        font=THEME["font_bold"], selectbackground=THEME["accent_blue"], bd=0, width=32)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self._on_note_select)

        # Right Note Editor
        right_col = tk.Frame(split, bg=THEME["bg_panel"], padx=18, pady=18)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        meta_row = tk.Frame(right_col, bg=THEME["bg_panel"])
        meta_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(meta_row, text="Title:", bg=THEME["bg_panel"], fg=THEME["fg_secondary"]).pack(side=tk.LEFT)
        self.note_title_ent = tk.Entry(meta_row, bg=THEME["bg_card"], fg=THEME["fg_primary"],
                                       insertbackground=THEME["fg_primary"], font=THEME["font_bold"], width=35, bd=0)
        self.note_title_ent.pack(side=tk.LEFT, padx=(6, 16), ipady=5)

        tk.Label(meta_row, text="Specialty:", bg=THEME["bg_panel"], fg=THEME["fg_secondary"]).pack(side=tk.LEFT)
        self.note_cat_ent = tk.Entry(meta_row, bg=THEME["bg_card"], fg=THEME["fg_primary"],
                                     insertbackground=THEME["fg_primary"], font=THEME["font_bold"], width=18, bd=0)
        self.note_cat_ent.pack(side=tk.LEFT, padx=6, ipady=5)

        tk.Button(meta_row, text="💾 Save Note", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=14, pady=5, command=self._save_current_note).pack(side=tk.RIGHT)

        self.note_editor = scrolledtext.ScrolledText(
            right_col, bg=THEME["bg_dark"], fg=THEME["fg_primary"],
            insertbackground=THEME["fg_primary"], font=THEME["font_mono"], wrap=tk.WORD, bd=0, padx=12, pady=12
        )
        self.note_editor.pack(fill=tk.BOTH, expand=True)

        self.selected_note_id = None
        self._refresh_notes_list()

    def _refresh_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        self.db.cursor.execute("SELECT id, title, category FROM study_notes ORDER BY id DESC")
        self.notes_cache = self.db.cursor.fetchall()
        for n in self.notes_cache:
            self.notes_listbox.insert(tk.END, f"[{n['category']}] {n['title']}")

    def _on_note_select(self, event):
        sel = self.notes_listbox.curselection()
        if not sel:
            return
        note_row = self.notes_cache[sel[0]]
        self.selected_note_id = note_row["id"]
        self.db.cursor.execute("SELECT * FROM study_notes WHERE id = ?", (self.selected_note_id,))
        full = self.db.cursor.fetchone()
        if full:
            self.note_title_ent.delete(0, tk.END)
            self.note_title_ent.insert(0, full["title"])
            self.note_cat_ent.delete(0, tk.END)
            self.note_cat_ent.insert(0, full["category"])
            self.note_editor.delete("1.0", tk.END)
            self.note_editor.insert(tk.END, full["content"])

    def _new_note_clear(self):
        self.selected_note_id = None
        self.note_title_ent.delete(0, tk.END)
        self.note_cat_ent.delete(0, tk.END)
        self.note_editor.delete("1.0", tk.END)

    def _save_current_note(self):
        t = self.note_title_ent.get().strip()
        c = self.note_cat_ent.get().strip() or "General"
        body = self.note_editor.get("1.0", tk.END).strip()
        if not t or not body:
            messagebox.showwarning("Missing Data", "Please enter both a Note Title and Content.")
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if self.selected_note_id:
            self.db.cursor.execute(
                "UPDATE study_notes SET title=?, category=?, content=?, updated_at=? WHERE id=?",
                (t, c, body, now, self.selected_note_id)
            )
        else:
            self.db.cursor.execute(
                "INSERT INTO study_notes (title, category, content, updated_at) VALUES (?, ?, ?, ?)",
                (t, c, body, now)
            )
        self.db.conn.commit()
        self._refresh_notes_list()
        messagebox.showinfo("Saved", f"Clinical note '{t}' saved successfully.")

    # ==========================================================================
    # MODULE 7: MEDICAL STUDY PLANNER
    # ==========================================================================
    def _build_planner_module(self, parent: tk.Frame):
        tk.Label(parent, text="📅 Clinical Rotation & Exam Study Planner",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(anchor="w", pady=(0, 12))

        # Quick Task Adder Bar
        add_bar = tk.Frame(parent, bg=THEME["bg_panel"], padx=15, pady=12)
        add_bar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(add_bar, text="Task:", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(side=tk.LEFT)
        self.plan_task_ent = tk.Entry(add_bar, width=32)
        self.plan_task_ent.pack(side=tk.LEFT, padx=(5, 12))

        tk.Label(add_bar, text="Subject:", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(side=tk.LEFT)
        self.plan_subj_ent = tk.Entry(add_bar, width=15)
        self.plan_subj_ent.pack(side=tk.LEFT, padx=(5, 12))

        tk.Label(add_bar, text="Due (YYYY-MM-DD):", bg=THEME["bg_panel"], fg=THEME["fg_primary"]).pack(side=tk.LEFT)
        self.plan_due_ent = tk.Entry(add_bar, width=12)
        self.plan_due_ent.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.plan_due_ent.pack(side=tk.LEFT, padx=(5, 12))

        self.plan_prio_var = tk.StringVar(value="High")
        ttk.Combobox(add_bar, textvariable=self.plan_prio_var, values=["High", "Medium", "Low"], width=8, state="readonly").pack(side=tk.LEFT, padx=5)

        tk.Button(add_bar, text="+ Add Task", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=14, pady=5, command=self._add_planner_task).pack(side=tk.RIGHT)

        # Planner Table
        cols = ("ID", "Task", "Subject", "Due Date", "Priority", "Status")
        self.planner_tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col, w in zip(cols, [50, 380, 140, 110, 100, 110]):
            self.planner_tree.heading(col, text=col)
            self.planner_tree.column(col, width=w)
        self.planner_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        action_bar = tk.Frame(parent, bg=THEME["bg_dark"])
        action_bar.pack(fill=tk.X)
        tk.Button(action_bar, text="✔ Toggle Completed / Pending", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=8, command=self._toggle_task_status).pack(side=tk.LEFT)
        tk.Button(action_bar, text="🗑 Delete Selected Task", bg=THEME["accent_red"], fg=THEME["fg_primary"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=8, command=self._delete_planner_task).pack(side=tk.LEFT, padx=12)

        self._refresh_planner()

    def _refresh_planner(self):
        for item in self.planner_tree.get_children():
            self.planner_tree.delete(item)
        self.db.cursor.execute("SELECT id, task, subject, due_date, priority, status FROM study_planner ORDER BY status DESC, due_date ASC")
        for r in self.db.cursor.fetchall():
            self.planner_tree.insert("", tk.END, iid=str(r["id"]),
                                     values=(r["id"], r["task"], r["subject"], r["due_date"], r["priority"], r["status"]))

    def _add_planner_task(self):
        t = self.plan_task_ent.get().strip()
        s = self.plan_subj_ent.get().strip() or "General"
        d = self.plan_due_ent.get().strip()
        p = self.plan_prio_var.get()
        if not t:
            return
        self.db.cursor.execute(
            "INSERT INTO study_planner (task, subject, due_date, priority, status) VALUES (?, ?, ?, ?, 'Pending')",
            (t, s, d, p)
        )
        self.db.conn.commit()
        self.plan_task_ent.delete(0, tk.END)
        self._refresh_planner()

    def _toggle_task_status(self):
        sel = self.planner_tree.selection()
        if not sel:
            return
        tid = int(sel[0])
        self.db.cursor.execute("SELECT status FROM study_planner WHERE id = ?", (tid,))
        curr = self.db.cursor.fetchone()["status"]
        new_st = "Completed" if curr == "Pending" else "Pending"
        self.db.cursor.execute("UPDATE study_planner SET status = ? WHERE id = ?", (new_st, tid))
        self.db.conn.commit()
        self._refresh_planner()

    def _delete_planner_task(self):
        sel = self.planner_tree.selection()
        if not sel:
            return
        self.db.cursor.execute("DELETE FROM study_planner WHERE id = ?", (int(sel[0]),))
        self.db.conn.commit()
        self._refresh_planner()

    # ==========================================================================
    # MODULE 8: MEDICAL TEXTBOOK & RESEARCH PDF READER
    # ==========================================================================
    def _build_pdf_module(self, parent: tk.Frame):
        top = tk.Frame(parent, bg=THEME["bg_dark"])
        top.pack(fill=tk.X, pady=(0, 12))

        tk.Label(top, text="📄 Medical PDF Textbook & Paper Reader",
                 bg=THEME["bg_dark"], fg=THEME["fg_primary"], font=THEME["font_title"]).pack(side=tk.LEFT)

        tk.Button(top, text="📂 Open PDF File", bg=THEME["accent_blue"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=6, command=self._open_pdf_file).pack(side=tk.RIGHT)
        tk.Button(top, text="➕ Save Selection as Note", bg=THEME["accent_green"], fg=THEME["bg_dark"],
                  font=THEME["font_bold"], bd=0, padx=16, pady=6, command=self._pdf_selection_to_note).pack(side=tk.RIGHT, padx=10)

        nav_bar = tk.Frame(parent, bg=THEME["bg_panel"], padx=15, pady=8)
        nav_bar.pack(fill=tk.X, pady=(0, 10))

        self.pdf_status_lbl = tk.Label(
            nav_bar,
            text="No PDF loaded. Click 'Open PDF File' to extract medical textbook chapters or research papers.",
            bg=THEME["bg_panel"], fg=THEME["fg_secondary"], font=THEME["font_bold"]
        )
        self.pdf_status_lbl.pack(side=tk.LEFT)

        tk.Button(nav_bar, text="Next Page ▶", bg=THEME["bg_card"], fg=THEME["fg_primary"],
                  bd=0, padx=12, command=lambda: self._step_pdf_page(1)).pack(side=tk.RIGHT, padx=4)
        tk.Button(nav_bar, text="◀ Prev Page", bg=THEME["bg_card"], fg=THEME["fg_primary"],
                  bd=0, padx=12, command=lambda: self._step_pdf_page(-1)).pack(side=tk.RIGHT, padx=4)

        self.pdf_text_view = scrolledtext.ScrolledText(
            parent, bg=THEME["bg_panel"], fg=THEME["fg_primary"],
            font=("Segoe UI", 11), wrap=tk.WORD, padx=20, pady=20, bd=0
        )
        self.pdf_text_view.pack(fill=tk.BOTH, expand=True)

        self.pdf_pages = []
        self.current_pdf_page = 0
        if not HAS_PYPDF:
            self.pdf_text_view.insert(
                tk.END,
                "💡 Optional Library Notice:\n"
                "To parse binary .pdf files, install pypdf via:\n"
                "    pip install pypdf\n\n"
                "You can also open .txt or .md clinical files directly with the Open button!"
            )

    def _open_pdf_file(self):
        path = filedialog.askopenfilename(
            title="Select Medical PDF or Text File",
            filetypes=[("PDF & Text Files", "*.pdf *.txt *.md"), ("All Files", "*.*")]
        )
        if not path:
            return

        self.pdf_pages = []
        self.current_pdf_page = 0

        if path.lower().endswith(".pdf"):
            if not HAS_PYPDF:
                messagebox.showwarning("pypdf Required", "Run 'pip install pypdf' in your terminal to read PDF files.")
                return
            try:
                reader = pypdf.PdfReader(path)
                for i, page in enumerate(reader.pages):
                    txt = page.extract_text() or f"[Page {i+1} contains scanned images or no extractable text]"
                    self.pdf_pages.append(txt)
            except Exception as e:
                messagebox.showerror("PDF Error", f"Could not read PDF:\n{e}")
                return
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                self.pdf_pages = [f.read()]

        self._render_pdf_page(os.path.basename(path))

    def _step_pdf_page(self, delta: int):
        if not self.pdf_pages:
            return
        self.current_pdf_page = max(0, min(len(self.pdf_pages) - 1, self.current_pdf_page + delta))
        self._render_pdf_page("Document")

    def _render_pdf_page(self, filename: str):
        if not self.pdf_pages:
            return
        self.pdf_status_lbl.configure(
            text=f"File: {filename}  •  Page {self.current_pdf_page + 1} of {len(self.pdf_pages)}"
        )
        self.pdf_text_view.delete("1.0", tk.END)
        self.pdf_text_view.insert(tk.END, self.pdf_pages[self.current_pdf_page])

    def _pdf_selection_to_note(self):
        try:
            selected = self.pdf_text_view.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
        except tk.TclError:
            selected = self.pdf_text_view.get("1.0", tk.END).strip()

        if not selected:
            messagebox.showinfo("Empty", "Highlight text or open a document first.")
            return

        title = f"PDF Extract ({datetime.datetime.now().strftime('%H:%M:%S')})"
        self.db.cursor.execute(
            "INSERT INTO study_notes (title, category, content, updated_at) VALUES (?, 'PDF Extract', ?, ?)",
            (title, selected[:4000], datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        self.db.conn.commit()
        messagebox.showinfo("Saved to Notes", f"Saved selection as '{title}' in Clinical Study Notes!")


# ==============================================================================
# 5. APPLICATION ENTRYPOINT
# ==============================================================================
if __name__ == "__main__":
    app = MedicalStudyAssistantApp()
    app.mainloop()
