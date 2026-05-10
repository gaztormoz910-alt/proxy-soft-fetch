import customtkinter as ctk

app = ctk.CTk()
tv = ctk.CTkTabview(app)
tv.add("tab1")
tv._segmented_button._buttons_dict["tab1"].configure(text="Translated Tab")
tv.set("tab1")
print("Set successfully")
