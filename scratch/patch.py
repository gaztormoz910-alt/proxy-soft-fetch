import re

with open("gui.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add LANG dictionary before ProxyHunterApp
lang_dict = """
LANG = {
    "EN": {
        "cfg": "Configuration",
        "lang_lbl": "Language:",
        "tab_settings": "⚡ Settings",
        "tab_countries": "🌍 Countries",
        "threads": "Threads",
        "timeout": "Timeout (sec)",
        "ping": "Max Ping (ms)",
        "speed": "Min Speed (Mbps)",
        "smtp": "Check SMTP",
        "res": "Residential Only",
        "all": "✓ All",
        "reset": "✗ Reset",
        "tier1": "Tier-1",
        "start": "▶ START HUNT",
        "running": "■ RUNNING...",
        "total": "Total Collected",
        "live": "Live Proxies",
        "elite": "Elite Proxies",
        "wait": "Waiting to start...",
        "step1": "Fetching from sources...",
        "step2": "Basic liveness check...",
        "step3": "Advanced filtering...",
        "step4": "Completed!",
        "tab_terminal": "📟 Terminal",
        "tab_results": "📋 Results",
        "proto": "Protocol",
        "ip": "IP Address",
        "port": "Port",
        "country": "Country",
        "copy": "📋 Copy",
        "refresh": "🔄 Refresh",
        "download": "📥 Download:",
        "csv": "CSV (Full)",
        "txt1": "TXT (IP:Port)",
        "txt2": "TXT (IP Only)",
        "copied": "✓ Copied!",
        "csv_saved": "✓ CSV saved!",
        "txt_saved": "✓ TXT saved!",
        "txt_ip_saved": "✓ TXT (IP) saved!",
        "no_data": "No data",
        "europe": "Europe"
    },
    "RU": {
        "cfg": "Конфигурация",
        "lang_lbl": "Язык:",
        "tab_settings": "⚡ Параметры",
        "tab_countries": "🌍 Страны",
        "threads": "Потоки (Threads)",
        "timeout": "Таймаут (сек)",
        "ping": "Макс Пинг (мс)",
        "speed": "Мин Скор. (Мбит/с)",
        "smtp": "Проверять SMTP",
        "res": "Только Residential",
        "all": "✓ Все",
        "reset": "✗ Сброс",
        "tier1": "Tier-1",
        "start": "▶ НАЧАТЬ СБОР",
        "running": "■ РАБОТАЕТ...",
        "total": "Всего собрано",
        "live": "Рабочие",
        "elite": "Элитные",
        "wait": "Ожидание запуска...",
        "step1": "Сбор из источников...",
        "step2": "Базовая проверка на живость...",
        "step3": "Расширенная фильтрация...",
        "step4": "Завершено!",
        "tab_terminal": "📟 Терминал",
        "tab_results": "📋 Результаты",
        "proto": "Протокол",
        "ip": "IP-адрес",
        "port": "Порт",
        "country": "Страна",
        "copy": "📋 Копировать",
        "refresh": "🔄 Обновить",
        "download": "📥 Скачать:",
        "csv": "CSV (Полный)",
        "txt1": "TXT (IP:Port)",
        "txt2": "TXT (Только IP)",
        "copied": "✓ Скопировано!",
        "csv_saved": "✓ CSV сохранен!",
        "txt_saved": "✓ TXT сохранен!",
        "txt_ip_saved": "✓ TXT (IP) сохранен!",
        "no_data": "Нет данных",
        "europe": "Европа"
    }
}
"""

code = code.replace("class ProxyHunterApp(ctk.CTk):", lang_dict + "\nclass ProxyHunterApp(ctk.CTk):")

# 2. Setup _t function and language variable
init_code = """
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
"""
init_replacement = """
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.current_lang = "RU"
        self.interactive_widgets = []
        
    def _t(self, key):
        return LANG[self.current_lang].get(key, key)
        
    def _set_language(self, lang):
        self.current_lang = lang
        self._apply_language()
        
    def _set_ui_state(self, state):
        for w in self.interactive_widgets:
            if w.winfo_exists():
                w.configure(state=state)
        # Also disable country checkboxes
        for var in self.country_vars.values():
            pass # We can't disable just the var, we need the checkbox widgets. Let's just disable the tabview so they can't switch to it.
        self.tab_view.configure(state=state)
                
    def _apply_language(self):
        self.lbl_cfg.configure(text="  " + self._t("cfg"))
        self.lbl_lang.configure(text=self._t("lang_lbl"))
        
        if hasattr(self, "lbl_threads"): self.lbl_threads.configure(text=self._t("threads"))
        if hasattr(self, "lbl_timeout"): self.lbl_timeout.configure(text=self._t("timeout"))
        if hasattr(self, "lbl_ping"): self.lbl_ping.configure(text=self._t("ping"))
        if hasattr(self, "lbl_speed"): self.lbl_speed.configure(text=self._t("speed"))
        
        if hasattr(self, "btn_all"): self.btn_all.configure(text=self._t("all"))
        if hasattr(self, "btn_reset"): self.btn_reset.configure(text=self._t("reset"))
        if hasattr(self, "btn_europe"): self.btn_europe.configure(text=self._t("europe"))
        if hasattr(self, "btn_tier1"): self.btn_tier1.configure(text=self._t("tier1"))
        
        self.smtp_switch.configure(text=self._t("smtp"))
        self.res_switch.configure(text=self._t("res"))
        
        if not self.is_running:
            self.start_btn.configure(text=self._t("start"))
        else:
            self.start_btn.configure(text=self._t("running"))
            
        self.lbl_stat_total.configure(text=self._t("total"))
        self.lbl_stat_live.configure(text=self._t("live"))
        self.lbl_stat_elite.configure(text=self._t("elite"))
        
        self.btn_copy.configure(text=self._t("copy"))
        self.btn_refresh.configure(text=self._t("refresh"))
        self.lbl_download.configure(text=self._t("download"))
        self.btn_csv.configure(text=self._t("csv"))
        self.btn_txt1.configure(text=self._t("txt1"))
        self.btn_txt2.configure(text=self._t("txt2"))
        
        self.proxy_tree.heading("proto", text=self._t("proto"))
        self.proxy_tree.heading("ip", text=self._t("ip"))
        self.proxy_tree.heading("port", text=self._t("port"))
        self.proxy_tree.heading("country", text=self._t("country"))
"""
code = code.replace(init_code, init_replacement)

# 3. Sidebar setup modifications
code = code.replace(
    'ctk.CTkLabel(header, text="  Configuration", font=("Segoe UI", 17, "bold"), text_color="white").pack(side="left")',
    'self.lbl_cfg = ctk.CTkLabel(header, text="  " + self._t("cfg"), font=("Segoe UI", 17, "bold"), text_color="white")\n        self.lbl_cfg.pack(side="left")'
)

# Language switcher
lang_switch_code = """
        lang_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        lang_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.lbl_lang = ctk.CTkLabel(lang_frame, text=self._t("lang_lbl"), font=("Segoe UI", 12), text_color=MUTED)
        self.lbl_lang.pack(side="left", padx=(0, 10))
        self.lang_seg = ctk.CTkSegmentedButton(lang_frame, values=["EN", "RU"], command=self._set_language, fg_color=BORDER, selected_color=BLUE, unselected_color=CARD)
        self.lang_seg.set("RU")
        self.lang_seg.pack(side="left", fill="x", expand=True)

        self.tab_view = ctk.CTkTabview(sidebar, fg_color=CARD2, segmented_button_fg_color=BORDER,
"""
code = code.replace('        self.tab_view = ctk.CTkTabview(sidebar, fg_color=CARD2, segmented_button_fg_color=BORDER,\n', lang_switch_code)


# Replacing switches to register them
code = code.replace(
    'ctk.CTkSwitch(frame, text="Check SMTP", variable=self.smtp_var, fg_color=BORDER,\n                       progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT).pack(anchor="w", padx=10, pady=4)',
    'self.smtp_switch = ctk.CTkSwitch(frame, text=self._t("smtp"), variable=self.smtp_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)\n        self.smtp_switch.pack(anchor="w", padx=10, pady=4)\n        self.interactive_widgets.append(self.smtp_switch)'
)

code = code.replace(
    'ctk.CTkSwitch(frame, text="Residential Only", variable=self.res_var, fg_color=BORDER,\n                       progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT).pack(anchor="w", padx=10, pady=4)',
    'self.res_switch = ctk.CTkSwitch(frame, text=self._t("res"), variable=self.res_var, fg_color=BORDER, progress_color=BLUE, font=("Segoe UI", 13), text_color=TEXT)\n        self.res_switch.pack(anchor="w", padx=10, pady=4)\n        self.interactive_widgets.append(self.res_switch)'
)

# Sliders tracking
code = code.replace(
    'slider = ctk.CTkSlider(parent, from_=from_, to=to,',
    'slider = ctk.CTkSlider(parent, from_=from_, to=to,'
)
code = code.replace(
    'entry.pack(side="left")',
    'entry.pack(side="left")\n        self.interactive_widgets.extend([slider, entry])'
)

# Quick countries buttons
code = code.replace(
    'ctk.CTkButton(quick, text="✓ Все",',
    'self.btn_all = ctk.CTkButton(quick, text=self._t("all"),'
)
code = code.replace(
    'command=self._select_all).pack',
    'command=self._select_all)\n        self.btn_all.pack'
)
code = code.replace(
    'ctk.CTkButton(quick, text="✗ Сброс",',
    'self.btn_reset = ctk.CTkButton(quick, text=self._t("reset"),'
)
code = code.replace(
    'command=self._deselect_all).pack',
    'command=self._deselect_all)\n        self.btn_reset.pack'
)
code = code.replace(
    'ctk.CTkButton(quick, text="Европа",',
    'self.btn_europe = ctk.CTkButton(quick, text=self._t("europe"),'
)
code = code.replace(
    'command=lambda: self._select_region("🇪🇺 Европа")).pack',
    'command=lambda: self._select_region("🇪🇺 Европа"))\n        self.btn_europe.pack'
)

code = code.replace(
    'ctk.CTkButton(quick, text="Tier-1",',
    'self.btn_tier1 = ctk.CTkButton(quick, text=self._t("tier1"),'
)
code = code.replace(
    'command=self._select_tier1).pack',
    'command=self._select_tier1)\n        self.btn_tier1.pack'
)

# Store slider labels
code = code.replace(
    'ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color=MUTED).pack(side="left")',
    'lbl = ctk.CTkLabel(row, text=self._t(attr), font=("Segoe UI", 12), text_color=MUTED)\n        lbl.pack(side="left")\n        setattr(self, f"lbl_{attr}", lbl)'
)


# Stats card modifications
code = code.replace(
    'self.stat_total = self._card(stats, "Total Collected", BLUE, "🌐", 0)',
    'self.stat_total, self.lbl_stat_total = self._card(stats, self._t("total"), BLUE, "🌐", 0)'
)
code = code.replace(
    'self.stat_live = self._card(stats, "Live Proxies", GREEN, "⚡", 1)',
    'self.stat_live, self.lbl_stat_live = self._card(stats, self._t("live"), GREEN, "⚡", 1)'
)
code = code.replace(
    'self.stat_elite = self._card(stats, "Elite Proxies", GOLD, "⭐", 2)',
    'self.stat_elite, self.lbl_stat_elite = self._card(stats, self._t("elite"), GOLD, "⭐", 2)'
)

code = code.replace(
    'def _card(self, parent, title, accent, emoji, col):',
    'def _card(self, parent, title, accent, emoji, col):'
)
code = code.replace(
    'ctk.CTkLabel(top, text=title, font=("Segoe UI", 12), text_color=MUTED).pack(side="left")',
    'lbl_title = ctk.CTkLabel(top, text=title, font=("Segoe UI", 12), text_color=MUTED)\n        lbl_title.pack(side="left")'
)
code = code.replace(
    'return lbl',
    'return lbl, lbl_title'
)

# Export buttons
code = code.replace(
    'ctk.CTkButton(toolbar, text="📋 Копировать",',
    'self.btn_copy = ctk.CTkButton(toolbar, text=self._t("copy"),'
)
code = code.replace('command=self._copy_results).pack', 'command=self._copy_results)\n        self.btn_copy.pack')

code = code.replace(
    'ctk.CTkButton(toolbar, text="🔄 Обновить",',
    'self.btn_refresh = ctk.CTkButton(toolbar, text=self._t("refresh"),'
)
code = code.replace('command=self._load_results).pack', 'command=self._load_results)\n        self.btn_refresh.pack')

code = code.replace(
    'ctk.CTkLabel(export_toolbar, text="📥 Скачать:",',
    'self.lbl_download = ctk.CTkLabel(export_toolbar, text=self._t("download"),'
)
code = code.replace('text_color=MUTED).pack', 'text_color=MUTED)\n        self.lbl_download.pack')

code = code.replace(
    'ctk.CTkButton(export_toolbar, text="CSV (Полный)",',
    'self.btn_csv = ctk.CTkButton(export_toolbar, text=self._t("csv"),'
)
code = code.replace('command=self._export_csv).pack', 'command=self._export_csv)\n        self.btn_csv.pack')

code = code.replace(
    'ctk.CTkButton(export_toolbar, text="TXT (IP:Port)",',
    'self.btn_txt1 = ctk.CTkButton(export_toolbar, text=self._t("txt1"),'
)
code = code.replace('command=self._export_txt_full).pack', 'command=self._export_txt_full)\n        self.btn_txt1.pack')

code = code.replace(
    'ctk.CTkButton(export_toolbar, text="TXT (Только IP)",',
    'self.btn_txt2 = ctk.CTkButton(export_toolbar, text=self._t("txt2"),'
)
code = code.replace('command=self._export_txt_ip).pack', 'command=self._export_txt_ip)\n        self.btn_txt2.pack')


# Border fix & Scrollbar
code = code.replace(
    'tree_frame = ctk.CTkFrame(parent, fg_color="#060B14", corner_radius=10, border_width=1, border_color=BORDER)',
    'tree_frame = ctk.CTkFrame(parent, fg_color="#060B14", corner_radius=10, border_width=0)'
)
code = code.replace(
    'scrollbar = tk.ttk.Scrollbar(tree_frame, orient="vertical", command=self.proxy_tree.yview)',
    'scrollbar = ctk.CTkScrollbar(tree_frame, orientation="vertical", command=self.proxy_tree.yview, fg_color="#060B14", button_color=BORDER, button_hover_color=MUTED)'
)

# Lock Config
code = code.replace(
    'def _run_hunter(self):',
    'def _run_hunter(self):'
)
code = code.replace(
    'self.is_running = True',
    'self.is_running = True\n        self._set_ui_state("disabled")'
)
code = code.replace(
    'self.start_btn.configure(text="■  RUNNING...", fg_color=RED, hover_color="#B91C1C")',
    'self.start_btn.configure(text=self._t("running"), fg_color=RED, hover_color="#B91C1C")'
)

code = code.replace(
    'self.is_running = False\n                self.after(0, lambda: self.start_btn.configure(text="▶  START HUNT", fg_color=BLUE, hover_color="#2563EB"))',
    'self.is_running = False\n                self.after(0, lambda: self._set_ui_state("normal"))\n                self.after(0, lambda: self.start_btn.configure(text=self._t("start"), fg_color=BLUE, hover_color="#2563EB"))'
)


# Tree view border removal layout
code = code.replace(
    'style.configure("Proxy.Treeview", background="#060B14", foreground=TEXT, fieldbackground="#060B14",\n                         font=("Consolas", 11), rowheight=26, borderwidth=0)',
    'style.configure("Proxy.Treeview", background="#060B14", foreground=TEXT, fieldbackground="#060B14",\n                         font=("Consolas", 11), rowheight=26, borderwidth=0, relief="flat")\n        style.layout("Proxy.Treeview", [("Proxy.Treeview.treearea", {"sticky": "nswe"})])'
)

with open("gui_patched.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patched gui_patched.py")
