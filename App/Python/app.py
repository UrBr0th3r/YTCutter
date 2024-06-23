
import customtkinter as ctk
from customtkinter import filedialog as fd
from typing import Callable, Union
from abc import ABC
import yt_dlp


from utils.Threads import *



dwl_dir = os.path.join(os.getenv("USERPROFILE"), "Downloads")


# yt_dlp_loc = r".\bin\yt-dlp.exe"

dbg = Debugger(False)

def bst(font_fam: str, text:str, dim:int, l:int, r:int) -> int:
    dbg.printfunc()
    if l == r-1:
        return l
    mid: int = (l+r)//2
    if ctk.CTkFont(font_fam, mid).measure(text) <= dim:
        return bst(font_fam, text, dim, mid, r)
    return bst(font_fam, text, dim, l, mid)

def get_maximum_font_dim(width: int, height: int, text: str, font: ctk.CTkFont) -> int:
    dbg.printfunc()
    base_dim: int = font.cget("size") # row height?
    family: str = font.cget("family")
    min_dim: int = 14
    if font.measure(text) <= width:
        print("Didnt changed the fot")
        return base_dim
    else:
        rows = ctk.CTkFont(family, min_dim).measure(text)//width +1
        new_dim = bst(family, text, width*rows, 14, base_dim)
        print(f"changed font to {new_dim}")
        return new_dim

        # controlla se con il font minimo e dividendo il testo in due con il width (wrapper), la dimensione della seconda riga
        # viene comunque superata. in caso 3 righe e così via, fino a raggiungere il massimo dell'altezza. in quel caso viene ridotto
        # anche il valore minimo
        # forse: splitta il testo con il wrap
    # forse: controlla anche che il testo non superi la dimensione massima d'altezza (abbassando anche sotto il valore minimo)






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



# CTK EXPANSIONS

class Label(ctk.CTkLabel, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, text:str, x:float, y:float, *, height:float = 0, color: str = None, relative_position: bool = False, relative_dimension: bool = False, wrap_length: int = 0, **kwargs):
        super().__init__(app, **kwargs)
        dbg.printfunc()

        self.x = x
        self.y = y
        self.rel_pos = relative_position
        self.app = app

        if wrap_length == 0:
            wrap_length = round(0.9*app.dim[0])
        self.wrap = wrap_length
        if color is not None:
            self.configure(text_color=color)
        if relative_dimension:
            height *= app.dim[1]
            wrap_length *= app.dim[0]

        if height != 0:
            self.configure(height=height)
        self.set_text(text)

    def set_text(self, text):
        """new_font = ctk.CTkFont(app.font.cget("family"), get_maximum_font_dim(self.wrap, 0, text, app.font))
        self.configure(font=new_font)"""
        dbg.printfunc()
        new_font = self.app.font
        to_check = text
        lines = []
        l = 0
        charI = 0
        lastDivI = 0
        endcheck = False
        while not endcheck:
            while l < self.wrap:
                charI += 1
                if charI >= len(to_check):
                    endcheck = True
                    lines.append(to_check)
                    break
                if to_check[charI] in "/_ ":
                    lastDivI = charI
                l = new_font.measure(to_check[:charI+1])
            else:
                lines.append(to_check[:lastDivI+1])
                to_check = to_check[lastDivI+1:]
                l = 0
                lastDivI = 0
                charI = 0
        text = "\n".join(lines)
        self.configure(text=text)
        # per ora ho fatto solo uno split del testo in nell'ultima posizione di split

class ProgressBar(ctk.CTkProgressBar, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, x:float, y:float, *, width:float = 0, height:float =0, color: str = None, relative_position: bool = False, relative_dimension: bool = False, starting_point:float = 0, **kwargs):
        super().__init__(app, **kwargs)
        dbg.printfunc()

        self.x = x
        self.y = y
        self.rel_pos = relative_position
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.configure(width=width)
        if height != 0:
            self.configure(height=height)
        if color is not None:
            self.configure(fg_color=color)
        self.set(starting_point)

class Entry(Methods, ctk.CTkEntry):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, x: float, y:float, *, width: float = 0, height: float = 0, bg_text: str = None, color: str = None, relative_position:bool = False, relative_dimension: bool = False, **kwargs):
        super().__init__(app, **kwargs)
        dbg.printfunc()

        self.x = x
        self.y = y
        self.rel_pos = relative_position
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.configure(width=width)
        if height != 0:
            self.configure(height=height)
        if bg_text is not None:
            self.configure(placeholder_text=bg_text)
        if color is not None:
            self.configure(background=color)



    def base_command(self, entry):
        print(f"you wrote {self.get()} ")

class Button(ctk.CTkButton, Methods):
    x:float
    y:float
    text:str
    rel_pos: bool
    grid_pos: bool
    extracted: str = None
    def __init__(self, app, text: str, x:float, y:float, *, width:float = 0, height:float = 0, color: str = None, command: Callable = None, relative_position: bool = False, relative_dimension: bool = False, grid_position: bool = False, **kwargs):
        super().__init__(app, text=text, **kwargs)
        dbg.printfunc()

        self.x = x
        self.y = y
        self.text = text
        self.rel_pos = relative_position
        self.grid_pos = grid_position
        if color is not None:
            self.configure(fg_color=color)
        if command is not None:
            self.configure(command=command)
        else:
            self.configure(command=lambda: self.base_command(text))
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.configure(width=width)
        if height != 0:
            self.configure(height=height)


    def base_command(self, name):
        print(f"{name} has been pressed.")





class OptionMenu(Methods, ctk.CTkOptionMenu):
    width:float = 200
    height: float = 40
    x:float
    y:float
    rel_pos:bool
    def __init__(self, app, values:list[str], x:float, y:float, width: float = 0, height: float = 0, color:str = None, title: str = "Select", command:Callable = None, *, relative_position:bool = False, relative_dimension: bool = False, **kwargs):
        super().__init__(app, values=values, **kwargs)
        dbg.printfunc()
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.width = width
        if height != 0:
            self.height = height
        self.configure(width=round(self.width), height=round(self.height))
        self.x = x
        self.y = y
        self.rel_pos = relative_position
        self.set(title)

        if color is not None:
            self.configure(fg_color=color)
            # altri colori ??
        if command is not None:
            self.configure(command=command)
        else:
            self.configure(command=self.base_command)


    def set_font(self, font:ctk.CTkFont):
        self.configure(font=font)
        self.configure(dropdown_font=font)
        #self.configure(width=font.cget("size")*10)


    def base_command(self, choice):
        print(f"{choice} has been selected")

class ScrollableFrame(Methods, ctk.CTkScrollableFrame):
    x: float
    y: float
    res_pos: bool
    def __init__(self, app, x:float, y:float, *, width: float = 0, height: float = 0, relative_position: bool = False, relative_dimension: bool = False, **kwargs):
        super().__init__(app, **kwargs)

        dbg.printfunc()
        self.x = x
        self.y = y
        self.res_pos = relative_position
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.configure(width=width)
        if height != 0:
            self.configure(height=height)
            self._scrollbar.configure(height=0)

        self.rel_place() if self.res_pos else self.abs_place()


# THREADS
"""
class DownloadThread(threading.Thread):
    def __init__(self, link: str, progress_bar: ProgressBar, app, label: Label = None):
        super().__init__()
        dbg.printfunc()
        self.link = link
        self.progress_bar = progress_bar
        self.label = label
        self.daemon = True
        self.app = app

    def run(self):
        dbg.printfunc()
        ytdl_opts = {
            'progress_hooks': [self.my_hook],
            "prefer_player": "ios"
        }
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                title = ydl.extract_info(self.link, download=False).get("title", None)
            title = title.replace(" ", "_").translate(str.maketrans("","", string.punctuation.replace("_", "")))+".mp4"
            self.dwl_loc: str = os.path.join(dwl_dir, title)
            # ytdl_opts["outtmpl"] = self.dwl_loc
            self.progress_bar.set(0)
            self.progress_bar.abs_place() if not self.progress_bar.rel_pos else self.progress_bar.rel_place()
            if self.label is not None:
                self.label.abs_place() if not self.label.rel_pos else self.label.rel_place()

            # Download
            self.what: int = 0
            tmp_video_path = os.path.join(dwl_dir, "video_tmp.mp4")
            tmp_audio_path = os.path.join(dwl_dir, "audio_tmp.m4a")
            # TODO: inserisci la scelta della qualità + cambia il download con un subprocesso che porta yt-dlp
            ytdl_opts["format"] = "bestvideo"
            ytdl_opts["outtmpl"] = tmp_video_path
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                ydl.download([self.link])
            self.what = 1
            ytdl_opts["format"] = "bestaudio"
            ytdl_opts["outtmpl"] = tmp_audio_path
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                ydl.download([self.link])
            # Merge
            # subprocess ffmpeg


            self.label.set_text(text=f"Video downloaded in {self.dwl_loc}")
            self.app.file_loc = self.dwl_loc
            self.progress_bar.place_forget()
        except yt_dlp.utils.DownloadError as e:
            self.label.rel_place()
            self.label.set_text("Error: Connection refused. Check your internet connection")
    def my_hook(self, d):
        if d['status'] == 'downloading':

            self.progress_bar.set(float(d['_percent_str'].strip('%'))/200 + 0.5*self.what)
            self.label.set_text(text=f"Downloading {"video" if self.what == 0 else "audio"}... {d['_percent_str']}  ETA: {d['_eta_str']}")
"""



class Popup(ctk.CTkToplevel):
    def __init__(self, app, dim:tuple[int, int], **kwargs):
        super().__init__(app, **kwargs)
        dbg.printfunc()
        self.dim = dim
        self.font = app.font


class PopupManager:
    popup = None
    popup_id = None
    def __init__(self, app, text:str, widgets: list[ctk.CTkBaseClass], dim:tuple[int, int] = (300,300)):
        dbg.printfunc()
        self.app = app
        self.text:str = text
        self.dim:tuple[int,int] = dim
        for widget in widgets:
            widget.bind("<Enter>", self.show_popup)
            widget.bind("<Leave>", self.hide_popup)



    def show_popup(self, event):
        dbg.printfunc()
        self.popup_id = self.app.after(1000, self.create_popup, event)
    def create_popup(self, event):
        dbg.printfunc()
        self.popup = Popup(self.app, self.dim, fg_color="#3b3b3b")
        self.popup.wm_overrideredirect(True)
        self.popup.geometry(f"+{event.x_root - (self.popup.cget('width')+10)}+{event.y_root + 10}") if self.dim == (0,0) else self.popup.geometry(f"{self.dim[0]}x{self.dim[1]}+{event.x_root -(self.dim[0]+10)}+{event.y_root +20}")
        label = ctk.CTkLabel(self.popup, text_color="#e5e5e5", text=self.text, wraplength=self.dim[0]-10)
        label.place(relx=0.5, rely=0.5, anchor="c")
    def hide_popup(self, event):
        dbg.printfunc()
        if self.popup_id:
            self.app.after_cancel(self.popup_id)
            self.popup_id = None
        if self.popup:
            self.popup.destroy()
            self.popup = None

class App(ctk.CTk):
    gui: dict[str, list[Union[Methods, Button, Entry]]]
    dim: tuple[int, int]
    font: ctk.CTkFont = None
    file_loc: str = None
    def __init__(self, dim: tuple[int, int], title: str, *, font: tuple[str, int] = None):
        super().__init__()
        dbg.printfunc()
        self.dim = dim
        self.geometry(f"{dim[0]}x{dim[1]}")
        self.resizable(False, False)
        self.title(title)
        if font is not None:
            self.font = ctk.CTkFont(font[0], font[1])
        ctk.set_default_color_theme("green")
        dbg.printdb("Set geometry, title and font")

        # general gui
        general_popup_text = """
How to use YTCutter:

Choose from the option menu:
download video from YT link OR choose video file from your computer

Then enter inside the text boxes: 
start / end of the period
(hover them to know how to parse)
To confirm: press "+"

After all of the ranges are set:
Press "Cut"
"""

        self.parse_popup_text = """
How to parse text:

Only seconds:
140 = 140s

Minutes:Seconds:
40:32 = 40min, 32s

Hours:Minutes:Seconds.Milliseconds:
1:00:23.324 = 3623s.324ms

REGEX:
^([0-9]{0,2}:)?([0-9]{0,2}:)?([0-9]{0,2})(.[0-9]*)?$
        """


        self.popup_button = Button(self, "?", 0.9, 0.1, width=dim[0]*0.05, height=dim[0]*0.05, relative_position=True, relative_dimension=False, state="disabled", color="#777777")
        self.popup_button.rel_place() if self.popup_button.rel_pos else self.popup_button.abs_place()
        self.popup = PopupManager(self, general_popup_text, [self.popup_button], dim=(300, 240))

        self.progress_bar = ProgressBar(self, 0.5, 0.7, width=0.9, relative_position=True, relative_dimension=True)
        self.label = Label(self, "Starting download ...", 0.5, 0.8, relative_position=True)

        # download gui
        self.link_entry = Entry(self, 0.3775, 0.25, width=0.68, height=0.1, relative_position=True, relative_dimension=True, bg_text="Enter video link...")
        self.link_entry.bind("<KeyRelease>", self.get_info)
        self.info_id = None
        self.yt_info: list[str] = []
        self.res = None
        self.icon_text = Label(self, "---", 540, 137, bg_color=self.link_entry.cget("fg_color"))
        self.download_button = Button(self, "Download", 0.8375, 0.225, width=0.25, height=0.05, relative_dimension=True, relative_position=True, command=self.download)#command=lambda: self.print_text_size("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.resolution_menu = OptionMenu(self, [], 0.8375, 0.275, width=0.25, height=0.05, relative_position=True, relative_dimension=True, title="Resolution", command=self.choose_res)
        #self.it.start()

        # file gui
        self.file_entry = Entry(self, 0.3775, 0.25, width=0.68, height=0.1, relative_position=True, relative_dimension=True, bg_text="Enter local video file...")
        self.file_entry.insert(0, "Browse file...")
        self.file_entry.configure(state="readonly")
        self.check_button = Button(self, "Browse", 0.8375, 0.25, width=0.25, height=0.1, relative_dimension=True, relative_position=True, command=self.select_file)

        # range gui: start end -> progress in scrollframe; progress bar will be a sum of n (#ranges) progress bar, all initialized like in trash.py
        self.scrollframe = ScrollableFrame(self, 0.45, 0.5, width=0.8, height=0.2, relative_position=True, relative_dimension=True)

        self.range_values: list[tuple[str | None, str | None]] = []
        self.add_widget()


        self.gui = {
            "Download": [
                self.link_entry,
                self.download_button,
                self.resolution_menu,
                self.icon_text
                #self.progress_bar,
                #self.dwl_label

            ],
            "File": [
                self.file_entry,
                self.check_button
            ]
        }
        # text = self.add_text(str(is_running_in_console()), 10, 10)

        self.optionMenu = OptionMenu(self, list(self.gui.keys()), 0.5, 0.1, relative_position=True, command=self.set_gui_on_change)
        self.optionMenu.abs_place() if not self.optionMenu.rel_pos else self.optionMenu.rel_place()




        #self.checkbox = self.add_optionmenu(list(self.gui.keys()), 0.5, 0.1, 1, relative_position=True, relative_dimensions=True, command=self.set_gui_on_change, color="red")
        #self.after(100, self.adjust, 600)
        self.cut_button = Button(self, "Cut", 0.9325, 0.5, width=0.1, height=0.22, relative_position=True, relative_dimension=True, command=self.cut)
        self.cut_button.rel_place()
        if font:
            self.set_font(self, self.font)

        dbg.printdb("Ended creating app")
        return
    def add_widget(self, orig_button: Button = None, start_link: Entry = None, end_link: Entry = None):
        dbg.printfunc()
        if orig_button is None:
            self.row = 0

        else:
            self.row = orig_button.y +1
        dim = self.scrollframe.cget("width")//10
        height = 35
        new_start = Entry(self.scrollframe, 0, self.row, width=dim*4, height=height, bg_text="Cut start...")
        new_start.configure(corner_radius=0, font=self.font)
        new_start.grid(column=new_start.x, row=new_start.y)
        new_end = Entry(self.scrollframe, 1, self.row, width=dim*4, height=height, bg_text="Cut end...")
        new_end.configure(corner_radius=0, font=self.font)
        new_end.grid(column=new_end.x, row=new_end.y)
        new_add = Button(self.scrollframe, "+", 2, self.row, width=dim*2, height=height)
        new_add.configure(corner_radius=0, font=self.font)
        new_add.grid(column=new_add.x, row=new_add.y)
        new_add.configure(command=lambda: self.add_widget(new_add, new_start, new_end))
        PopupManager(self, self.parse_popup_text, [new_start, new_end], dim=(220, 200))
        if orig_button is not None:
            orig_button.configure(fg_color=("#911f1f"), text="-", command=lambda: self.remove_widgets(self.scrollframe,orig_button.y), hover_color="#cc2d2d")
            start = start_link.get() if start_link.get() != "" else None
            end = end_link.get() if end_link.get() != "" else None
            if (start, end) not in self.range_values:
                self.range_values.append((start, end))
            if start is None:
                start_link.delete(0, ctk.END)
                start_link.insert(0, "From the start")
            if end is None:
                end_link.delete(0, ctk.END)
                end_link.insert(0, "To the end")
            start_link.configure(state="readonly")
            end_link.configure(state="readonly")
            print(self.range_values)
        #     pulsante.configure(state="disabled", fg_color=("gray", "darkgray"))
    def remove_widgets(self, grid_frame, row_rem):
        dbg.printfunc()
        for widget in grid_frame.grid_slaves(row=row_rem):
            widget.grid_forget()
        self.range_values.pop(row_rem)

    def download(self):
        dbg.printfunc()
        if self.link_entry.get() == "":
            self.label.set_text("Error: enter a link")
            self.label.rel_place() if self.label.rel_pos else self.label.rel_place()
            return
        if self.res is None:
            self.label.set_text("Error: choose a resolution")
            self.label.rel_place() if self.label.rel_pos else self.label.rel_place()
            return
        try:
            extracted = self.link_entry.get()
        except yt_dlp.utils.DownloadError as e:
            self.label.set_text(f"Error: {str(e)}")
            self.label.rel_place() if self.label.rel_pos else self.label.abs_place()
            return
        # print(f"{self.text}: self.extracted set to {self.extracted}")
        self.thr = DownloadThread(extracted, os.path.join(dwl_dir, self.yt_info[0]), self.res, self.yt_info[1], self, self.progress_bar, self.label)
        self.thr.start()

        self.res = None

        # RESET ICON TEXT TO ---, block link_entry and empty it after

    def select_file(self):
        dbg.printfunc()
        self.file_loc = fd.askopenfilename()
        self.file_entry.configure(state="normal")
        self.file_entry.delete(0, ctk.END)
        self.file_entry.insert(0, self.file_loc)
        self.file_entry.configure(state="readonly")
    def cut(self):
        dbg.printfunc()
        if len(self.range_values) == 0 or all(rng == (None, None) for rng in self.range_values):
            self.label.set_text("Cannot cut: you didn't insert any range, or your ranges are all from start to end")
            self.label.rel_place()

        elif not self.file_loc:
            self.label.set_text("Cannot cut: No file nor downloaded video selected")
            self.label.rel_place()
        else:
            trm = VideoTrimmer(self, self.progress_bar, self.label, self.file_loc, self.range_values)
            trm.start()
    def get_info(self, event):
        self.canary = False
        if self.info_id is not None:
            self.after_cancel(self.info_id)
        if self.link_entry.get() != "":
            self.info_id = self.after(500, self.infoThUpd)
        else:
            self.icon_text.set_text("---")
            self.icon_text.configure(text_color="gray")

    def infoThUpd(self):
        self.canary = True
        self.it = InfoThread(self.link_entry.get(), self, self.resolution_menu, self.icon_text)
        self.it.start()
    def choose_res(self, choice):
        if choice not in ["Best", "Fast", "Fastest"]:
            self.res = self.yt_info[2][choice]
        else:
            self.res = choice

    def set_font(self, parent, font: ctk.CTkFont):
        dbg.printfunc()
        for widget in parent.winfo_children():
            try:
                widget.set_font(font)
            except Exception as e:
                print(f"Cannot set font for {widget}: {e}")
            if widget.winfo_children():
                self.set_font(widget, font)

    def set_gui_on_change(self, choice):
        dbg.printfunc()
        for spec_GUI in self.gui.values():
            for widget in spec_GUI:
                widget.place_forget()
                widget.pack_forget()

        for widget in self.gui[choice]:
            if not widget.rel_pos:
                widget.abs_place()
            else:
                widget.rel_place()
    def print_text_size(self, text: str):
        dbg.printfunc()
        print(self.font.measure(text))

    def close(self):

        self.destroy()
        # Doing: block closing app if thread are active



if __name__ == "__main__":


    dbg.printdb("Started program")
    app = App((800, 600), "YTCutter", font=("Arial", 20))
    dbg.printdb("App done")
    # app.iconbitmap(path/to/icon.ico)
    app.mainloop()
    app.protocol("WM_DELETE_WINDOW", app.close)
    try:
        if app.it.is_alive():
            app.it.stop()
    except AttributeError:
        pass
    try:
        if app.thr.is_alive():
            app.thr.stop()
    except AttributeError:
        pass

# TODO: gestire i millisecondi come .000 mentre 1.1.1 vuol dire: 1h, 1m, 1s + setup wizard + git lfs
#  aggiungere:
#  nella sezione file, fai che l'entry di scelta del file è modificabile, e controlla se il file scritto è valido. in caso può essere anche scelto con browse. crea un bottone sotto a browse che è proprio OK, che blocca la entry (fino a che non viene tagliato il video)


# TODO: aggiungi i requirements.text sia al python App, sia al python CLI
