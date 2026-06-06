import sys
import os
import re

GUI_FILE = r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\gui.py'
FETCH_FILE = r'c:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy\fetch_proxy.py'

# 1. Update gui.py translations
with open(GUI_FILE, 'r', encoding='utf-8') as f:
    gui_content = f.read()

gui_content = gui_content.replace(
    '"chk_clean": "✨ Clean"',
    '"chk_clean": "✨ Clean",\n        "output_dir_lbl": "Save Folder:",\n        "output_dir_btn": "Browse"'
)

gui_content = gui_content.replace(
    '"chk_clean": "✨ Чистый"',
    '"chk_clean": "✨ Чистый",\n        "output_dir_lbl": "Папка сохранения:",\n        "output_dir_btn": "Выбрать"'
)

# 2. Inject UI elements in gui.py _build_settings_tab
ui_snippet = """        # Output Directory
        ctk.CTkFrame(frame, fg_color=BORDER, height=1).pack(fill="x", padx=10, pady=12)
        out_frame = ctk.CTkFrame(frame, fg_color="transparent")
        out_frame.pack(fill="x", padx=10, pady=4)
        
        if not hasattr(self, "output_dir"):
            self.output_dir = tk.StringVar(value=os.getcwd())
            
        self.lbl_out_dir = ctk.CTkLabel(out_frame, text=self._t("output_dir_lbl"), font=("Segoe UI", 12, "bold"), text_color=MUTED)
        self.lbl_out_dir.pack(anchor="w", pady=(0, 5))
        
        dir_inner = ctk.CTkFrame(out_frame, fg_color="transparent")
        dir_inner.pack(fill="x")
        
        # Text color white so it's readable when disabled (using a trick or just read-only)
        self.entry_out_dir = ctk.CTkEntry(dir_inner, textvariable=self.output_dir, state="readonly", fg_color="#060B14", border_color=BORDER, text_color="#E2E8F0")
        self.entry_out_dir.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_out_dir = ctk.CTkButton(dir_inner, text=self._t("output_dir_btn"), width=60, fg_color=CARD2, hover_color=BORDER, command=self._select_output_dir)
        self.btn_out_dir.pack(side="left")
        self.interactive_widgets.append(self.btn_out_dir)

        # Spacer + HW info"""

gui_content = gui_content.replace(
    '        # Spacer + HW info',
    ui_snippet
)

# Add _select_output_dir method
method_snippet = """
    def _select_output_dir(self):
        from tkinter import filedialog as fd
        path = fd.askdirectory(title=self._t("output_dir_lbl"), initialdir=self.output_dir.get())
        if path:
            self.output_dir.set(path)

    def _build_settings_tab"""

gui_content = gui_content.replace(
    '    def _build_settings_tab',
    method_snippet
)

# 3. Pass output_dir to ProxyHunter in gui.py
gui_content = gui_content.replace(
    'random_counts=random_counts_val',
    'random_counts=random_counts_val,\n                    output_dir=self.output_dir.get()'
)

with open(GUI_FILE, 'w', encoding='utf-8') as f:
    f.write(gui_content)

# 4. Update fetch_proxy.py
with open(FETCH_FILE, 'r', encoding='utf-8') as f:
    fetch_content = f.read()

fetch_content = re.sub(
    r'def __init__\(self, threads=100, timeout=5, countries=None, max_ping=500, min_speed=1\.0,\s*check_smtp=True, collect_dc=True, collect_res=True, collect_mob=True, random_counts=None\):',
    r'def __init__(self, threads=100, timeout=5, countries=None, max_ping=500, min_speed=1.0, check_smtp=True, collect_dc=True, collect_res=True, collect_mob=True, random_counts=None, output_dir="."):',
    fetch_content
)

fetch_content = re.sub(
    r'self\.random_counts = random_counts or \{\}',
    r'self.random_counts = random_counts or {}\n        self.output_dir = output_dir',
    fetch_content
)

fetch_content = fetch_content.replace(
    'def _save_category(self, folder_name: str, results_list: List[str], description: str):\n        os.makedirs(folder_name, exist_ok=True)',
    'def _save_category(self, folder_name: str, results_list: List[str], description: str):\n        full_path = os.path.join(self.output_dir, folder_name)\n        os.makedirs(full_path, exist_ok=True)'
)

fetch_content = fetch_content.replace(
    'with open(os.path.join(folder_name, \'all.txt\'),',
    'with open(os.path.join(full_path, \'all.txt\'),'
)
fetch_content = fetch_content.replace(
    'with open(os.path.join(folder_name, \'all.csv\'),',
    'with open(os.path.join(full_path, \'all.csv\'),'
)

with open(FETCH_FILE, 'w', encoding='utf-8') as f:
    f.write(fetch_content)

print("Updates applied successfully.")
