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
    
