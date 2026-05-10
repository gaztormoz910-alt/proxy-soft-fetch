with open("gui.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Fix _load_results
code = code.replace("ISO_TO_NAME.get(row[3], row[3])", "ISO_TO_NAME[self.current_lang].get(row[3], row[3])")

# 2. Fix _export_csv
code = code.replace("ISO_TO_NAME.get(vals[3], vals[3])", "ISO_TO_NAME[self.current_lang].get(vals[3], vals[3])")

# 3. Fix _build_countries_tab
code = code.replace("self._pending_regions = list(REGIONS.items())", "self._pending_regions = list(REGIONS[self.current_lang].items())")

# 4. Fix _select_region
code = code.replace("if region_name in REGIONS:", "if region_name in REGIONS[self.current_lang]:")
code = code.replace("for iso in REGIONS[region_name]:", "for iso in REGIONS[self.current_lang][region_name]:")

# 5. Fix _select_tier1
tier_code = """    def _select_tier1(self):
        self._deselect_all()
        # Tier-1 ISO codes
        tier1 = {"US", "CA", "GB", "DE", "FR", "NL", "AU", "SE", "CH", "JP", "SG"}
        for iso, var in self.country_vars.items():
            if iso in tier1:
                var.set(1)
        self._update_country_count()"""

# We just find the method and replace it. Or replace its loop? Wait, _select_tier1 only uses country_vars, it doesn't use REGIONS! Let's check.
# Let's see if _build_countries_tab is called multiple times.
# If user switches language, _build_countries_tab might need to be rebuilt?
# Yes! `_apply_language` does NOT rebuild `_build_countries_tab`.
# If the user opens countries, it builds it in the current language. If they switch language, it stays in the old language!
# Wait! I need to destroy and rebuild countries tab on language switch.
'''
        if hasattr(self, "tab_view") and self._countries_built:
            # We must rebuild the countries tab so that country names are updated
            # the easiest way is to destroy the scrollable frame and rebuild it.
            if hasattr(self, "_country_scroll"):
                self._country_scroll.destroy()
                self._countries_built = False
                # Re-select the tab will trigger build again
'''
# Actually, I can just write a script that adds a check to `_apply_language`

with open("gui.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated ISO_TO_NAME and REGIONS references!")
