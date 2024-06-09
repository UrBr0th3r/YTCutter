import customtkinter as ctk
from customtkinter import filedialog as fd
from typing import Callable, Union
from abc import ABC
import threading
import yt_dlp
from moviepy.editor import VideoFileClip
from proglog import ProgressBarLogger
import os
import string
from time import time, sleep

dwl_dir = os.path.join(os.getenv("USERPROFILE"), "Downloads")

def bst(font_fam: str, text:str, dim:int, l:int, r:int) -> int:
    if l == r-1:
        return l
    mid: int = (l+r)//2
    if ctk.CTkFont(font_fam, mid).measure(text) <= dim:
        return bst(font_fam, text, dim, mid, r)
    return bst(font_fam, text, dim, l, mid)

def get_maximum_font_dim(width: int, height: int, text: str, font: ctk.CTkFont) -> int:
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
    width:int = 200
    x:float
    y:float
    rel_pos:bool
    def __init__(self, app, values:list[str], x:float, y:float, color:str = None, command:Callable = None, *, relative_position:bool = False, **kwargs):
        super().__init__(app, values=values, width=self.width, height=40, **kwargs)
        self.x = x
        self.y = y
        self.rel_pos = relative_position
        self.set("Select")

        if color is not None:
            self.configure(fg_color=color)
            # altri colori ??
        if command is not None:
            self.configure(command=command)
        else:
            self.configure(command=self.base_command)

        self.abs_place() if not self.rel_pos else self.rel_place()

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
        super().__init__(app, **kwargs) # , width=400, height=700)
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

class DownloadThread(threading.Thread):
    def __init__(self, link: str, progress_bar: ProgressBar, app, label: Label = None):
        threading.Thread.__init__(self)
        self.link = link
        self.progress_bar = progress_bar
        self.label = label
        self.daemon = True
        self.app = app

    def run(self):
        ytdl_opts = {
            'progress_hooks': [self.my_hook],
            "format": "bestvideo+bestaudio/best",
            "prefer_player": "ios"
        }
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                title = ydl.extract_info(self.link, download=False).get("title", None)
            title = title.replace(" ", "_").translate(str.maketrans("","", string.punctuation.replace("_", "")))+".mp4"
            self.dwl_loc: str = os.path.join(dwl_dir, title)
            ytdl_opts["outtmpl"] = self.dwl_loc
            self.progress_bar.abs_place() if not self.progress_bar.rel_pos else self.progress_bar.rel_place()
            if self.label is not None:
                self.label.abs_place() if not self.label.rel_pos else self.label.rel_place()
            self.progress_bar.set(0)
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                ydl.download([self.link])
            self.label.set_text(text=f"Video downloaded in {self.dwl_loc}")
            self.app.file_loc = self.dwl_loc
            self.progress_bar.place_forget()
        except yt_dlp.utils.DownloadError as e:
            self.label.rel_place()
            self.label.set_text("Error: Connection refused. Check your internet connection")
    def my_hook(self, d):
        if d['status'] == 'downloading':

            self.progress_bar.set(float(d['_percent_str'].strip('%'))/100)
            self.label.set_text(text=f"Downloading... {d['_percent_str']}  ETA: {d['_eta_str']}")

class MyBarLogger(ProgressBarLogger):
    def __init__(self, app, progress_var, label_var):
        super().__init__()
        self.app = app
        self.progress_var = progress_var
        self.label_var: Label = label_var
        self.last_message = ''
        self.previous_percentage = 0
        self.time = 0
        self.idx = 0
        self.name = ""
    def update_time(self, time):
        self.time = time
    def update_idx(self, idx):
        self.idx = idx
    def update_name(self, name):
        self.name = name

    def callback(self, **changes):
        for parameter, value in changes.items():
            self.last_message = value

    def bars_callback(self, bar, attr, value, old_value=None):
        if 'Writing video' in self.last_message:
            percentage = (value / self.bars[bar]['total']) * 100
            if percentage > 0 and percentage <= 100:
                if int(percentage) != self.previous_percentage:
                    ETAs = round((time()-self.time)*(100-percentage)/percentage)
                    ETA = f"{ETAs//3600:02d}:{(ETAs%3600)//60:02d}:{ETAs%60:02d}"
                    self.previous_percentage = int(percentage)
                    self.label_var.set_text(f'Cutting #{self.idx+1}: {round(percentage, 2)}% ; ETA: {ETA}')
                    self.progress_var.set(percentage/100)
                    self.app.update_idletasks()



class VideoTrimmer(threading.Thread):
    def __init__(self, app, progbar: ProgressBar, label: Label, video_file: str, ranges: list[tuple[str, str]]):
        threading.Thread.__init__(self)
        self.master = app
        self.progress_bar = progbar
        self.label = label
        self.video_file: str = video_file
        self.daemon = True
        self.range_values = ranges
        self.logger = MyBarLogger(self.master, self.progress_bar, self.label)

    def run(self) -> None:
        for rngIdx in range(len(self.range_values)):

            self.trim_video(self.range_values[rngIdx][0], self.range_values[rngIdx][1], rngIdx)
            sleep(1)
            # trm.setup(self.range_values[rngIdx][0], self.range_values[rngIdx][1], rngIdx)
            # trm.start()
        for rowN in range(self.master.row+1):
            try:
                self.master.remove_widgets(self.master.scrollframe, rowN)
            except IndexError:
                pass
        self.master.add_widget()


    def trim_video(self, start_ins: str | None, end_ins: str | None, idx: int):
        self.logger.update_time(time())
        self.logger.update_idx(idx)
        # Open the video file
        clip = VideoFileClip(self.video_file)
        start_time: float
        end_time: float
        try:
            if start_ins is None:
                start_time = 0.0
            else:
                start_ops = start_ins.split(".")
                if len(start_ops) == 1:
                    start_time = float(start_ops[0])
                elif len(start_ops) > 3:
                    raise ValueError("Too many argument in start time")
                else:
                    start_time = (float(start_ops[0])* 60 if start_ops[0] != "" else 0) + (float(start_ops[1]) if start_ops[1] != "" else 0)
                    try:
                        start_time += float(start_ops[2])/pow(10, len(start_ops[2]))
                    except IndexError:
                        pass

            if end_ins is None:
                end_time = clip.duration
            else:
                end_ops = end_ins.split(".")
                if len(end_ops) == 1:
                    end_time = float(end_ops[0])
                elif len(end_ops) > 3:
                    raise ValueError("Too many argument in end time")
                else:
                    end_time = (float(end_ops[0]) * 60 if end_ops[0] != "" else 0) + (
                        float(end_ops[1]) if end_ops[1] != "" else 0)
                    try:
                        end_time += float(end_ops[2]) / pow(10, len(end_ops[2]))
                    except IndexError:
                        pass
            if start_time >= end_time:
                raise ValueError("Start time is bigger than end time")


            # Trim the video
            trimmed_clip = clip.subclip(start_time, end_time)

            # Write the trimmed video to a new file
            title = self.video_file[:self.video_file.rindex(".mp4")]+f"_[{start_ins if start_ins else 'Start'}-{end_ins if end_ins else 'End'}].mp4"
            self.logger.update_name(title)
            self.label.set_text("Starting to cut...")
            self.label.rel_place() if self.label.rel_pos else self.label.abs_place()
            self.progress_bar.set(0)
            self.progress_bar.rel_place() if self.progress_bar.rel_pos else self.progress_bar.abs_place()

            trimmed_clip.write_videofile(title, logger=self.logger)

            # Close the video file
            trimmed_clip.close()
            self.label.set_text(f"Cut #{idx + 1} saved in: {title}")

            #self.label.set_text(f"Cut #{idx+1}: Saved in {title}")
        except ValueError as e:
            self.label.set_text(f"Error: {str(e)}")
            self.label.rel_place() if self.label.rel_pos else self.label.abs_place()
        finally:
            clip.close()


class Popup(ctk.CTkToplevel):
    def __init__(self, app, dim:tuple[int, int], **kwargs):
        super().__init__(app, **kwargs)
        self.dim = dim
        self.font = app.font


class PopupManager:
    popup = None
    popup_id = None
    def __init__(self, app, text:str, widgets: list[ctk.CTkBaseClass], dim:tuple[int, int] = (300,300)):
        self.app = app
        self.text:str = text
        self.dim:tuple[int,int] = dim
        for widget in widgets:
            widget.bind("<Enter>", self.show_popup)
            widget.bind("<Leave>", self.hide_popup)



    def show_popup(self, event):
        self.popup_id = self.app.after(500, self.create_popup, event)
    def create_popup(self, event):
        self.popup = Popup(self.app, self.dim, fg_color="#3b3b3b")
        self.popup.wm_overrideredirect(True)
        self.popup.geometry(f"+{event.x_root - (self.popup.cget('width')+10)}+{event.y_root + 10}") if self.dim == (0,0) else self.popup.geometry(f"{self.dim[0]}x{self.dim[1]}+{event.x_root -(self.dim[0]+10)}+{event.y_root +20}")
        label = ctk.CTkLabel(self.popup, text_color="#e5e5e5", text=self.text, wraplength=self.dim[0]-10)
        label.place(relx=0.5, rely=0.5, anchor="c")
    def hide_popup(self, event):
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
        self.dim = dim
        self.geometry(f"{dim[0]}x{dim[1]}")
        self.resizable(False, False)
        self.title(title)
        if font is not None:
            self.font = ctk.CTkFont(font[0], font[1])
        ctk.set_default_color_theme("green")

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

Minutes.Seconds:
40.32 = 40min.32s

Minutes.Seconds.Milliseconds:
00.23.324 = 23s.324ms
        """

        self.popup_button = Button(self, "?", 0.9, 0.1, width=dim[0]*0.05, height=dim[0]*0.05, relative_position=True, relative_dimension=False, state="disabled", color="#777777")
        self.popup_button.rel_place() if self.popup_button.rel_pos else self.popup_button.abs_place()
        self.popup = PopupManager(self, general_popup_text, [self.popup_button], dim=(300, 240))

        self.progress_bar = ProgressBar(self, 0.5, 0.7, width=0.9, relative_position=True, relative_dimension=True)
        self.label = Label(self, "Starting download ...", 0.5, 0.8, relative_position=True)

        # download gui
        self.link_entry = Entry(self, 0.3775, 0.25, width=0.68, height=0.1, relative_position=True, relative_dimension=True, bg_text="Enter YouTube link...")
        self.download_button = Button(self, "Download", 0.8375, 0.25, width=0.25, height=0.1, relative_dimension=True, relative_position=True, command=self.download)#command=lambda: self.print_text_size("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

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

        #self.checkbox = self.add_optionmenu(list(self.gui.keys()), 0.5, 0.1, 1, relative_position=True, relative_dimensions=True, command=self.set_gui_on_change, color="red")
        #self.after(100, self.adjust, 600)
        self.cut_button = Button(self, "Cut", 0.9325, 0.5, width=0.1, height=0.22, relative_position=True, relative_dimension=True, command=self.cut)
        self.cut_button.rel_place()
        if font:
            self.set_font(self, self.font)

        return
    def add_widget(self, orig_button: Button = None, start_link: Entry = None, end_link: Entry = None):
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
        for widget in grid_frame.grid_slaves(row=row_rem):
            widget.grid_forget()
        self.range_values.pop(row_rem)

    def download(self):
        extracted = self.link_entry.get()
        # print(f"{self.text}: self.extracted set to {self.extracted}")
        if any(x not in extracted for x in ["youtu", ".", "/"]):
            raise ValueError("Bad link")
        thr = DownloadThread(extracted, self.progress_bar, self, self.label)
        thr.start()

    def select_file(self):
        self.file_loc = fd.askopenfilename()
        self.file_entry.configure(state="normal")
        self.file_entry.delete(0, ctk.END)
        self.file_entry.insert(0, self.file_loc)
        self.file_entry.configure(state="readonly")
    def cut(self):

        if len(self.range_values) == 0 or all(rng == (None, None) for rng in self.range_values):
            self.label.set_text("Cannot cut: you didn't insert any range, or your ranges are all from start to end")
            self.label.rel_place()

        elif not self.file_loc:
            self.label.set_text("Cannot cut: No file nor downloaded video selected")
            self.label.rel_place()
        else:
            trm = VideoTrimmer(self, self.progress_bar, self.label, self.file_loc, self.range_values)
            trm.start()






    def set_font(self, parent, font: ctk.CTkFont):
        for widget in parent.winfo_children():
            try:
                widget.set_font(font)
            except Exception as e:
                print(f"Cannot set font for {widget}: {e}")
            if widget.winfo_children():
                self.set_font(widget, font)

    def set_gui_on_change(self, choice):
        for spec_GUI in self.gui.values():
            for widget in spec_GUI:
                widget.place_forget()
                widget.grid_forget()
                widget.pack_forget()

        for widget in self.gui[choice]:
            if not widget.rel_pos and not widget.grid_pos:
                widget.abs_place()
            elif widget.rel_pos:
                widget.rel_place()
            else:
                widget.grid_place()
    def print_text_size(self, text: str):
        print(self.font.measure(text))



if __name__ == "__main__":
    app = App((800, 600), "YTCutter", font=("Arial", 20))
    print("App done")
    app.mainloop()
