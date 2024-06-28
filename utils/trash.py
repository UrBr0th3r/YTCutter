"""import subprocess, json
link = "https://www.youtube.com/watch?v=a6XM2TKqNfw"
command = f"../bin/yt-dlp --dump-json {link}".split()

proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True)
stdout, stderr = proc.communicate()
if stderr:
    print(f"Errori:\n{stderr}")
js = json.loads(stdout)


resolutions = {f.get("format_id"): f.get("resolution") for f in js.get("formats", [])}

for key in resolutions.keys():
    print(key, resolutions[key], type(key))"""
import os.path

"""import subprocess, json

command = (f".\\bin\\yt-dlp.exe https://www.youtube.com/watch?v=3_X_Hd1XpXE -J").split()
proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)

while True:
    output = proc.stdout.readline()
    error = None
    if output == '' and proc.poll() is not None:
        break
    if output:

        js = json.loads(output.strip())
        print({f.get("resolution"): f.get("format_id") for f in js.get("formats", []) if f["ext"] == "webm"})
"""
"""from PIL import ImageTk, Image
import customtkinter as ctk
from abc import ABC

class Methods(ABC):
    x:float
    y:float
    font: ctk.CTkFont
    def abs_place(self):
        self.place(x=round(self.x), y=round(self.y))
    def rel_place(self):
        self.place(relx=self.x, rely=self.y, anchor="c")
    def grid_place(self):
        self.grid(column=round(self.x), row=round(self.y))

    def set_font(self, font:ctk.CTkFont):
        self.configure(font=font)

class Canvas(ctk.CTkCanvas, Methods):
    def __init__(self, app, x: float, y: float, width: float, height: float, relative_position: bool = False,
                 relative_dimension: bool = False, **kwargs):
        super().__init__(app, **kwargs)
        self.x = x
        self.y = y
        self.rel_pos = relative_position
        self.app = app
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        self.configure(width=round(width), height=round(height))
        self.images = []
        self.rel_place() if self.rel_pos else self.abs_place()

    def rectangle(self, x: float, y: float, width: float, height: float, color: str, rel_pos: bool = False,
                  rel_dim: bool = False, alpha: float = 1):
        if rel_pos:
            x *= self.app.dim[0]
            y *= self.app.dim[1]
        if rel_dim:
            width *= self.app.dim[0]
            height *= self.app.dim[1]
        rAlpha = round(alpha * 255)
        rColor = self.app.winfo_rgb(color) + (rAlpha,)
        img = Image.new("RGBA", (round(width), round(height)), rColor)
        self.images.append(ImageTk.PhotoImage(img))
        self.create_image(round(x), round(y), image=self.images[-1], anchor="nw")
        #self.create_rectangle(x, y, width+x, height+y)

app = ctk.CTk()
app.geometry("500x500")
app.dim = (500, 500)
cnv = Canvas(app, .5, .5, 1, 1, relative_position=True, relative_dimension=True)
cnv.rectangle(50, 50, 100, 200, "#ff0000")
cnv.rectangle(10, 10, 200, 150, "#00ff00", alpha=.5)
app.mainloop()
"""
import os
