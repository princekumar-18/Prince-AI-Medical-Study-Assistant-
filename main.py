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
