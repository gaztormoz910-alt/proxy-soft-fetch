import sys
import re

with open('gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: bind <Configure>
content = content.replace(
    'self.bind_all("<Button-1>", self._on_click_outside)',
    'self.bind_all("<Button-1>", self._on_click_outside)\n        self.bind("<Configure>", self._on_configure)\n        \n    def _on_configure(self, event):\n        if event.widget == self:\n            self._is_moving = True\n            if hasattr(self, "_moving_timer"):\n                self.after_cancel(self._moving_timer)\n            self._moving_timer = self.after(300, self._stop_moving)\n            \n    def _stop_moving(self):\n        self._is_moving = False'
)

# Fix 2: Start_hunter realtime proxies init
content = content.replace(
    'self.result_count_lbl.configure(text=self._t("proxies_count").format(0))',
    'self.result_count_lbl.configure(text=self._t("proxies_count").format(0))\n        # [AUDIT FIX] Initialize realtime data immediately\n        self.realtime_proxies = {"live": [], "elite": []}\n        self._live_count = 0\n        self._elite_count = 0'
)

# Fix 3: _flush_log smart freeze + queue fix + terminal batching
old_flush = '''    def _flush_log(self):
        """Сбрасываем накопленные логи в терминал каждые 200мс"""
        with self._log_lock:
            batch = []
            for _ in range(min(50, len(self._log_buffer))):
                batch.append(self._log_buffer.popleft())
            
            p_queue = self._proxy_queue[:500]
            self._proxy_queue = self._proxy_queue[500:]'''

new_flush = '''    def _flush_log(self):
        """Сбрасываем накопленные логи в терминал каждые 200мс"""
        if getattr(self, '_is_moving', False):
            self.after(200, self._flush_log)
            return
            
        with self._log_lock:
            batch = []
            self._log_tick = getattr(self, '_log_tick', 0) + 1
            if self._log_tick % 5 == 0:
                for _ in range(min(150, len(self._log_buffer))):
                    batch.append(self._log_buffer.popleft())
            
            p_queue = self._proxy_queue
            self._proxy_queue = []'''
content = content.replace(old_flush, new_flush)

# Fix 4: _drain_queues batch insert capped to 5000
old_drain_insert = '''            inserted = 0
            for data, source in p_queue:
                self.realtime_proxies[source].append(data)
                
                if mapped_src == source:
                    if current_filter == "all" or current_filter == data["protocol"].lower():
                        if hasattr(self, "proxy_tree"):
                            country_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                            self.proxy_tree.insert("", "end", values=(data["protocol"], data["ip"], data["port"], country_name))
                            inserted += 1
                            
            if inserted > 0:
                children = self.proxy_tree.get_children()
                if len(children) > 5000:
                    self.proxy_tree.delete(*children[:-5000])'''

new_drain_insert = '''            new_matching = []
            for data, source in p_queue:
                self.realtime_proxies[source].append(data)
                if mapped_src == source:
                    if current_filter == "all" or current_filter == data["protocol"].lower():
                        if hasattr(self, "proxy_tree"):
                            country_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                            new_matching.append((data["protocol"], data["ip"], data["port"], country_name))
                            
            if new_matching:
                if len(new_matching) >= 5000:
                    self.proxy_tree.delete(*self.proxy_tree.get_children())
                    for vals in new_matching[-5000:]:
                        self.proxy_tree.insert("", "end", values=vals)
                else:
                    for vals in new_matching:
                        self.proxy_tree.insert("", "end", values=vals)
                    children = self.proxy_tree.get_children()
                    if len(children) > 5000:
                        self.proxy_tree.delete(*children[:-5000])'''
content = content.replace(old_drain_insert, new_drain_insert)

# Fix 5: _load_results realtime reading
old_load = '''        self._current_raw_data = []
        protos, countries = set(), set()

        if self.is_running and hasattr(self, "realtime_proxies"):
            data_list = self.realtime_proxies.get(mapped_src, [])
            for data in data_list:
                c_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                self._current_raw_data.append((data["protocol"].upper(), data["ip"], data["port"], c_name))
                protos.add(data["protocol"].upper())
                countries.add(c_name)
        else:'''
new_load = '''        if self.is_running and hasattr(self, "realtime_proxies"):
            self.proxy_tree.delete(*self.proxy_tree.get_children())
            data_list = self.realtime_proxies.get(mapped_src, [])
            for data in data_list[-5000:]:
                c_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                self.proxy_tree.insert("", "end", values=(data["protocol"].upper(), data["ip"], data["port"], c_name))
            
            real_count = getattr(self, '_live_count' if mapped_src == 'live' else '_elite_count', 0)
            if real_count == 0:
                self.result_count_lbl.configure(text=self._t("no_data"))
                if hasattr(self, "results_empty_lbl"):
                    self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
            else:
                disp_text = f" {real_count} "
                if real_count > 5000:
                    disp_text = f" {real_count} (показаны последние 5000) "
                self.result_count_lbl.configure(text=self._t("proxies_count").format(disp_text))
                if hasattr(self, "results_empty_lbl"):
                    self.results_empty_lbl.place_forget()
            return
            
        self._current_raw_data = []
        protos, countries = set(), set()
        
        if not self.is_running:'''
content = content.replace(old_load, new_load)

# Fix 6: _apply_filters reading
old_apply_filters = '''        for proto, ip, port, country in getattr(self, "_current_raw_data", []):
            match_proto = not sel_protos or len(sel_protos) == len(self.all_protos_in_db) or proto in sel_protos
            match_country = not sel_countries or len(self.all_countries_in_db) == len(self.all_countries_in_db) or country in sel_countries
            
            if match_proto and match_country:
                self.proxy_tree.insert("", "end", values=(proto, ip, port, country))
                count += 1'''
new_apply_filters = '''        if self.is_running and hasattr(self, "realtime_proxies"):
            source = self.result_source.get()
            mapped_src = "live" if source.lower() in ("live", self._t("source_live").lower()) else "elite"
            data_list = self.realtime_proxies.get(mapped_src, [])
            filtered_data = []
            for data in data_list:
                proto = data["protocol"].upper()
                c_name = ISO_TO_NAME[self.current_lang].get(data["country"], data["country"])
                match_proto = not sel_protos or len(sel_protos) == len(self.all_protos_in_db) or proto in sel_protos
                match_country = not sel_countries or len(sel_countries) == len(self.all_countries_in_db) or c_name in sel_countries
                if match_proto and match_country:
                    filtered_data.append((proto, data["ip"], data["port"], c_name))
            
            for vals in filtered_data[-5000:]:
                self.proxy_tree.insert("", "end", values=vals)
            
            real_count = getattr(self, '_live_count' if mapped_src == 'live' else '_elite_count', 0)
            if real_count == 0:
                self.result_count_lbl.configure(text=self._t("no_data"))
                if hasattr(self, "results_empty_lbl"):
                    self.results_empty_lbl.place(relx=0.5, rely=0.5, anchor="center")
            else:
                disp_text = f" {real_count} "
                if real_count > 5000:
                    disp_text = f" {real_count} (показаны последние 5000) "
                self.result_count_lbl.configure(text=self._t("proxies_count").format(disp_text))
                if hasattr(self, "results_empty_lbl"):
                    self.results_empty_lbl.place_forget()
            return

        for proto, ip, port, country in getattr(self, "_current_raw_data", []):
            match_proto = not sel_protos or len(sel_protos) == len(self.all_protos_in_db) or proto in sel_protos
            match_country = not sel_countries or len(sel_countries) == len(self.all_countries_in_db) or country in sel_countries
            
            if match_proto and match_country:
                if count < 5000:
                    self.proxy_tree.insert("", "end", values=(proto, ip, port, country))
                count += 1'''
content = content.replace(old_apply_filters, new_apply_filters)

exports_str = '''    def _get_filtered_data_for_export(self):
        sel_protos = self.selected_protos
        sel_countries = self.selected_countries
        filtered = []
        for proto, ip, port, country in getattr(self, "_current_raw_data", []):
            match_proto = not sel_protos or len(sel_protos) == len(self.all_protos_in_db) or proto in sel_protos
            match_country = not sel_countries or len(sel_countries) == len(self.all_countries_in_db) or country in sel_countries
            if match_proto and match_country:
                filtered.append((proto, ip, port, country))
        return filtered

    def _copy_results(self):
        lines = []
        for vals in self._get_filtered_data_for_export():
            lines.append(f"{vals[0].lower()}://{vals[1]}:{vals[2]}")
        if lines:
            self.clipboard_clear()
            self.clipboard_append("\\n".join(lines))
            self.result_count_lbl.configure(text=self._t("copied"))
            self.after(2000, self._apply_filters)

    def _export_csv(self):
        data = self._get_filtered_data_for_export()
        if not data: return
        import csv
        path = fd.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title=self._t("save_csv_title"))
        if not path: return
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Протокол', 'IP', 'Port', 'Страна'])
            for vals in data:
                writer.writerow([vals[0].upper(), vals[1], vals[2], vals[3]])
        self.result_count_lbl.configure(text=self._t("csv_saved"))

    def _export_txt_proto(self):
        data = self._get_filtered_data_for_export()
        if not data: return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("save_txt_proto_title"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for vals in data:
                f.write(f"{vals[0].lower()}://{vals[1]}:{vals[2]}\\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_full(self):
        data = self._get_filtered_data_for_export()
        if not data: return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("save_txt1_title"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            for vals in data:
                f.write(f"{vals[1]}:{vals[2]}\\n")
        self.result_count_lbl.configure(text=self._t("txt_saved"))

    def _export_txt_ip(self):
        data = self._get_filtered_data_for_export()
        if not data: return
        path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title=self._t("save_txt2_title"))
        if not path: return
        with open(path, 'w', encoding='utf-8') as f:
            ips = set()
            for vals in data:
                ips.add(vals[1])
            for ip in sorted(ips):
                f.write(f"{ip}\\n")
        self.result_count_lbl.configure(text=self._t("txt_ip_saved"))'''

content = re.sub(r'    def _copy_results\(self\):.*?txt_ip_saved\"\)\)', exports_str, content, flags=re.DOTALL)

with open('gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
