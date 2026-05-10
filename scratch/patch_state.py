with open("gui.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Remove self.tab_view.configure(state=state)
code = code.replace("self.tab_view.configure(state=state)", "# self.tab_view.configure(state=state)")

# 2. Add quick buttons to interactive_widgets
code = code.replace("self.btn_tier1.pack(side=\"left\", padx=2)", 
'''self.btn_tier1.pack(side="left", padx=2)
        self.interactive_widgets.extend([self.btn_all, self.btn_reset, self.btn_europe, self.btn_tier1])''')

# 3. Add checkboxes to interactive_widgets
target_checkbox = """            cb = ctk.CTkCheckBox(grid, text=f"{name} ({iso})", variable=var,
                             fg_color=BORDER, hover_color="#2D3748", checkmark_color="white",
                             border_color=BORDER, font=("Segoe UI", 11), text_color=TEXT,
                             command=self._update_count, width=150
                             )
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=1)
            self.interactive_widgets.append(cb)"""

original_checkbox = """            ctk.CTkCheckBox(grid, text=f"{name} ({iso})", variable=var,
                             fg_color=BORDER, hover_color="#2D3748", checkmark_color="white",
                             border_color=BORDER, font=("Segoe UI", 11), text_color=TEXT,
                             command=self._update_count, width=150
                             ).grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=1)"""

code = code.replace(original_checkbox, target_checkbox)

# 4. Add "Все" button in region headers to interactive_widgets
target_btn = """        btn = ctk.CTkButton(hdr, text="Все", width=36, height=20, fg_color=BLUE, hover_color="#2563EB",
                       font=("Segoe UI", 10), corner_radius=4,
                       command=lambda rn=region_name: self._select_region(rn))
        btn.pack(side="right", padx=5, pady=3)
        self.interactive_widgets.append(btn)"""

original_btn = """        ctk.CTkButton(hdr, text="Все", width=36, height=20, fg_color=BLUE, hover_color="#2563EB",
                       font=("Segoe UI", 10), corner_radius=4,
                       command=lambda rn=region_name: self._select_region(rn)).pack(side="right", padx=5, pady=3)"""

code = code.replace(original_btn, target_btn)

# Write back
with open("gui.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated GUI interactive state logic!")
