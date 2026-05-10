import customtkinter as ctk

app = ctk.CTk()
tv = ctk.CTkTabview(app)
tv.add("tab1")
print(tv._segmented_button._buttons_dict["tab1"].cget("text"))
