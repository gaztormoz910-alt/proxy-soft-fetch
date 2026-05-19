import customtkinter as ctk

app = ctk.CTk()
app.geometry("400x400")

scroll = ctk.CTkScrollableFrame(app, fg_color="red")
scroll.pack(fill="both", expand=True)

inner = ctk.CTkFrame(scroll, fg_color="blue", height=100)
inner.pack(fill="x")

def stretch(e):
    canvas = scroll._parent_canvas
    frame = scroll._parent_frame
    req_h = frame.winfo_reqheight()
    h = e.height
    print(f"Canvas height: {h}, req_h: {req_h}")
    if h > req_h:
        canvas.itemconfig(scroll._parent_canvas_window_id, height=h)
    else:
        canvas.itemconfig(scroll._parent_canvas_window_id, height="")

scroll.bind("<Configure>", stretch)

app.update()
print("Stretching height to 400 manually...")
scroll._parent_canvas.itemconfig(scroll._parent_canvas_window_id, height=400)
app.update()
print(f"Frame height after stretch: {scroll._parent_frame.winfo_height()}")

app.destroy()
