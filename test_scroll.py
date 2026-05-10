import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x400")

def check_scrollbar(*args):
    # inner frame height
    inner_h = frame._parent_frame.winfo_reqheight()
    # canvas (visible area) height
    canvas_h = frame._parent_canvas.winfo_height()
    print(f"Inner: {inner_h}, Canvas: {canvas_h}")
    if inner_h > canvas_h and canvas_h > 10:
        frame._scrollbar.grid(row=0, column=1, sticky="ns")
    else:
        frame._scrollbar.grid_remove()

frame = ctk.CTkScrollableFrame(app)
frame.pack(fill="both", expand=True)

frame._parent_canvas.bind("<Configure>", check_scrollbar, add="+")
frame._parent_frame.bind("<Configure>", check_scrollbar, add="+")

btn = ctk.CTkButton(app, text="Add Label", command=lambda: ctk.CTkLabel(frame, text="Hello").pack())
btn.pack()

app.mainloop()
