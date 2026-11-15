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
