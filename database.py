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

