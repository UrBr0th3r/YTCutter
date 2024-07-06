from PIL import Image, ImageTk
import customtkinter as ctk
from customtkinter import filedialog as fd
from typing import Callable, Union
from abc import ABC
import yt_dlp


from utils.Threads import *



dwl_dir = os.path.join(os.getenv("USERPROFILE"), "Downloads")


# yt_dlp_loc = r".\bin\yt-dlp.exe"

dbg = Debugger(False)



def set_font(parent, font: ctk.CTkFont):
    dbg.printfunc()
    for widget in parent.winfo_children():
        try:
            widget.set_font(font)
        except Exception as e:
            print(f"Cannot set font for {widget}: {e}")
        if widget.winfo_children():
            set_font(widget, font)

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
        print("Didn't changed the font")
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
    rel_pos: bool
    def abs_place(self):
        dbg.printfunc()
        self.place(x=round(self.x), y=round(self.y))
    def rel_place(self):
        dbg.printfunc()

        self.place(relx=self.x, rely=self.y, anchor="c")
    def grid_place(self):
        dbg.printfunc()

        self.grid(column=round(self.x), row=round(self.y))

    def set_font(self, font:ctk.CTkFont):
        dbg.printfunc()
        self.configure(font=font)
    def kplace(self):
        self.rel_place() if self.rel_pos else self.abs_place()



# CTK EXPANSIONS

class Frame(ctk.CTkFrame, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, x: float, y: float, width: float, height: float, relative_position: bool = False, relative_dimension: bool = False, **kwargs):
        super().__init__(app, **kwargs)
        self.x = x
        self.y = y
        self.rel_pos = relative_position
        self.font = app.font
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        self.dim = (width, height)

        self.configure(width=round(width), height=round(height))


class Label(ctk.CTkLabel, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, text:str, x:float, y:float, *, height:float = 0, color: str = None, relative_position: bool = False, relative_dimension: bool = False, wrap_length: int = 0, force_text: bool = False, **kwargs):
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
        if force_text:
            self.configure(text=text)
        else:
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
        self.create_rectangle(x, y, width + x, height + y)

    def create_round_consecutive_line(self, points: list[tuple[int, int]], width: int = 1, color: str = "gray", **kwargs):
        for i in range(1, len(points)):
            self.create_oval(points[i-1][0]-width/2, points[i-1][1]-width/2, points[i-1][0]+width/2-1, points[i-1][1]+width/2-1, fill=color, outline=color, **kwargs)
            self.create_line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], fill=color, width=width, **kwargs)
            self.create_oval(points[i][0]-width/2, points[i][1]-width/2, points[i][0]+width/2-1, points[i][1]+width/2-1, fill=color, outline=color, **kwargs)
    def ping_animation(self, points: list[tuple[int, int]], width: int = 1, color: str = "gray"):
        # doing: anim
        raise NotImplementedError




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
    width: float = 200
    height: float = 40
    x:float
    y:float
    rel_pos:bool
    def __init__(self, app, values:list[str], x:float, y:float, width: float = 0, height: float = 0, color:str = None, title: str = "Select", command:Callable = None, *, relative_position:bool = False, relative_dimension: bool = False, dinamic_width: bool = False, font: ctk.CTkFont = None, **kwargs):
        super().__init__(app, values=values, **kwargs)
        dbg.printfunc()
        self.dinamic_width = dinamic_width
        if not font:
            font = app.font
        self.font = font
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.width = width
        elif dinamic_width:
            self.set_dinamic_width(values)
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

    def set_dinamic_width(self, new_vals):
        try:
            self.width = 0.45 * max([self.font.measure(val) for val in new_vals]) + 160
        except ValueError:
            self.width = 200
        self.configure(width=round(self.width))
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



class Popup(ctk.CTkToplevel):
    def __init__(self, app, dim:tuple[int, int], **kwargs):
        super().__init__(app, **kwargs)
        dbg.printfunc()
        self.dim = dim

class PopupManager:
    popup = None
    popup_id = None
    def __init__(self, app, text:str, widgets: list[ctk.CTkBaseClass], dim:tuple[int, int] = None, time: int = 1000, font: ctk.CTkFont = None):
        dbg.printfunc()
        self.app = app
        self.text:str = text
        self.time = time
        if not font:
            font = app.font
        self.font = font

        # calculate optimal dimensions
        if not dim:
            lines = text.split("\n")
            width = max([self.font.measure(line) for line in lines])+40
            height = len(lines)*self.font.cget("size")+40
            dim = (width, height)

        self.dim:tuple[int,int] = dim
        for widget in widgets:
            widget.bind("<Enter>", self.show_popup)
            widget.bind("<Leave>", self.hide_popup)





    def show_popup(self, event):
        dbg.printfunc()
        self.popup_id = self.app.after(self.time, self.create_popup, event)
    def create_popup(self, event):
        dbg.printfunc()
        self.popup = Popup(self.app, self.dim, fg_color="#3b3b3b")
        self.popup.wm_overrideredirect(True)
        self.popup.geometry(f"{self.dim[0]}x{self.dim[1]}+{event.x_root -(self.dim[0]+10)}+{event.y_root +20}")
        label = ctk.CTkLabel(self.popup, text_color="#e5e5e5", text=self.text, wraplength=self.dim[0]-10, font=self.font)
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
    def __init__(self):
        # CHECK: usa il main label per mostrare le informazioni "di percorso": piazzalo all'inizio e cambia ciò
        #  che c'è scritto in base all'operazione scelta
        super().__init__()

        dim = (800, 600)
        title = "YTCutter"
        font = ("Arial", 20)

        dbg.printfunc()
        self.dim = dim
        self.geometry(f"{dim[0]}x{dim[1]}")

        iconpath = ImageTk.PhotoImage(file="..\\..\\utils\\ico\\download.ico")
        self.wm_iconbitmap()
        self.iconphoto(False, iconpath)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.resizable(False, False)
        self.title(title)
        if font is not None:
            self.font = ctk.CTkFont(font[0], font[1])
        ctk.set_default_color_theme("green")
        ctk.set_appearance_mode("dark")
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

        self.parse_popup_text = r"""
How to parse text:

Only seconds:
140 = 140s

Minutes:Seconds:
40:32 = 40min, 32s

Hours:Minutes:Seconds.Milliseconds:
1:00:23.324 = 3623s.324ms

REGEX:
^(?:(\d+):)?(?:(\d+):)?(\d+)(\.\d+)?$
        """

        # relative positions
        pad = 0.05
        blockend = 0.6
        button_width = 0.25625
        entry_height = 0.1
        opt_width = 0.25
        opt_height = 0.05
        pop_dim = opt_height * dim[1]
        icon_width = (entry_height*dim[1]/dim[0])
        entry_width = 1-2*pad-icon_width-button_width
        scroll_width = 1-2*pad-button_width+icon_width
        scroll_height = blockend-(pad+opt_height+3*entry_height)
        cut_width = 1 - 2*pad - scroll_width - icon_width
        entry_x = pad + entry_width / 2
        entry_y = pad+opt_height+3*entry_height/2
        icon_x = pad+entry_width+icon_width/2
        button_x = pad+entry_width+icon_width+button_width/2
        opt_x = button_x-button_width/2-3*icon_width- opt_width/2
        opt_y = pad+opt_height/2
        pop_x = opt_x + opt_width/2 + icon_width + opt_height/2
        scroll_x = pad + scroll_width/2
        scroll_y = blockend - scroll_height/2
        cut_x = 1 - pad - cut_width/2
        progbar_y = 0.7

        cnv = Canvas(self, 0, 0, width=dim[0], height=dim[1], background="gray14", highlightcolor="gray14", highlightthickness=0, bd=0)
        cnv.pack()
        line_col = "gray"
        anim_col = "green"
        line_dim = 6
        cnv.create_round_consecutive_line([
            (round((pop_x-opt_height/2-icon_width/2)*dim[0]), round((opt_y-entry_height/2)*dim[1])),
            (round((pop_x-opt_height/2-icon_width/2)*dim[0]), round((opt_y+entry_height/2+opt_height/2)*dim[1])),
            (round(icon_x*dim[0]), round((opt_y+entry_height/2+opt_height/2)*dim[1])),
            (round(icon_x*dim[0]), round((entry_y+entry_height)*dim[1])),
            (round((cut_x-cut_width/2-icon_width/2)*dim[0]), round((entry_y+entry_height)*dim[1])),
            (round((cut_x-cut_width/2-icon_width/2)*dim[0]), round((progbar_y-entry_height/2)*dim[1]))
        ], width=line_dim, color=line_col)

        self.popup_button = Button(self, "?", pop_x, opt_y, width=pop_dim, height=pop_dim, relative_position=True, relative_dimension=False, state="disabled", color="#777777")
        self.popup_button.rel_place() if self.popup_button.rel_pos else self.popup_button.abs_place()
        PopupManager(self, general_popup_text, [self.popup_button], time=100)



        self.progress_bar = ProgressBar(self, 0.5, progbar_y, width=0.9, relative_position=True, relative_dimension=True)
        self.progress_bar.rel_place()
        self.label = Label(self, "Choose an option", 0.5, 0.8, relative_position=True)
        self.label.rel_place() if self.label.rel_pos else self.label.abs_place()


        # download gui
        self.link_entry = Entry(self, entry_x, entry_y, width=entry_width, height=entry_height, relative_position=True, relative_dimension=True, bg_text="Enter video link...")
        self.link_entry.bind("<KeyRelease>", self.get_info)
        self.info_id = None
        self.yt_info: list[str] = []
        self.res = None
        self.download_button = Button(self, "Download", button_x, entry_y-entry_height/4, width=button_width+2/dim[0], height=entry_height/2, relative_dimension=True, relative_position=True, command=self.download, border_color=self.cget("fg_color"), border_width=1)
        self.resolution_menu = OptionMenu(self, [], button_x, entry_y+entry_height/4, width=button_width, height=entry_height/2, relative_position=True, relative_dimension=True, title="Resolution", command=self.choose_res)

        # file gui
        self.file_entry = Entry(self, entry_x, entry_y, width=entry_width, height=entry_height, relative_position=True, relative_dimension=True, bg_text="Enter local video file...")
        self.file_entry.bind("<KeyRelease>", self.file_check)
        self.file_id = None
        self.check_button = Button(self, "Browse", button_x, entry_y, width=button_width, height=entry_height, relative_dimension=True, relative_position=True, command=self.select_file)

        # range gui: start end -> progress in scrollframe; progress bar will be a sum of n (#ranges) progress bar, all initialized like in trash.py
        self.scrollframe = ScrollableFrame(self, scroll_x-6/dim[0], scroll_y, width=scroll_width-18/dim[0], height=scroll_height-12/dim[1], relative_position=True, relative_dimension=True, fg_color="gray14")
        self.icon_text = Label(self, "---", icon_x, entry_y, relative_position=True)
        self.range_values: list[tuple[str | None, str | None]] = []
        self.add_widget()

        # fr = ctk.CTkFrame(self, width=round(icon_width*dim[0]), height=round(scroll_height*dim[1]), fg_color="red")
        # fr.place(relx=scroll_x+scroll_width/2+icon_width/2, rely=scroll_y, anchor="c")


        self.gui = {
            "Download": [
                self.link_entry,
                self.download_button,
                self.resolution_menu,
                self.icon_text,
                "Enter a video link in the entry bar"
                #self.progress_bar,
                #self.dwl_label

            ],
            "File": [
                self.file_entry,
                self.check_button,
                self.icon_text,
                "Choose a file from your device"
            ]
        }
        # text = self.add_text(str(is_running_in_console()), 10, 10)

        self.optionMenu = OptionMenu(self, list(self.gui.keys()), opt_x, opt_y, width=opt_width, height=pad, relative_position=True, relative_dimension=True, command=self.set_gui_on_change)
        self.optionMenu.abs_place() if not self.optionMenu.rel_pos else self.optionMenu.rel_place()




        #self.checkbox = self.add_optionmenu(list(self.gui.keys()), 0.5, 0.1, 1, relative_position=True, relative_dimensions=True, command=self.set_gui_on_change, color="red")
        #self.after(100, self.adjust, 600)
        self.cut_button = Button(self, "Cut", cut_x, scroll_y, width=cut_width, height=scroll_height, relative_position=True, relative_dimension=True, command=self.cut)
        self.cut_button.rel_place()
        if font:
            set_font(self, self.font)
        self.icon_text.set_font(ctk.CTkFont("Arial", 30))


        dbg.printdb("Ended creating app")
        return


    def add_widget(self, orig_button: Button = None, start_link: Entry = None, end_link: Entry = None):
        dbg.printfunc()
        if orig_button is None:
            self.row = 0

        else:
            self.row = orig_button.y +1
        dim = self.scrollframe.cget("width")//10
        height = 40
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
        PopupManager(self, self.parse_popup_text, [new_start, new_end], time=1000)
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
        #self.file_entry.configure(state="normal")
        self.file_entry.delete(0, ctk.END)
        self.file_entry.insert(0, self.file_loc)
        #self.file_entry.configure(state="readonly")
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
            self.file_entry.delete(0, ctk.END)
            self.link_entry.delete(0, ctk.END)
    def get_info(self, event):

        if self.info_id is not None:
            self.after_cancel(self.info_id)
        if self.link_entry.get() != "":
            self.info_id = self.after(500, self.infoThUpd, "Link")
        else:
            self.icon_text.set_text("---")
            self.icon_text.configure(text_color="gray")
    def file_check(self, event):

        if self.file_id is not None:
            self.after_cancel(self.file_id)
        if self.file_entry.get() != "":
            self.file_id = self.after(50, self.infoThUpd, "File")
        else:
            self.icon_text.set_text("---")
            self.icon_text.configure(text_color="gray")

    def infoThUpd(self, mode: str):
        if hasattr(self, "it") and self.it.is_alive():
            print(f"STOP InfoThread: changed {self.it.newlink} to {self.link_entry.get()}")
            self.it.stop()
        if mode == "Link":
            self.it = InfoThread(self.link_entry.get(), self, self.resolution_menu, self.icon_text)
            self.it.start()
        elif mode == "File":
            self.it = FileInfoThread(self.file_entry.get(), self, self.icon_text)
            self.it.start()
        else:
            raise ValueError(f"Error: infoThUpd {mode=} is wrong")
        # ERROR: il thread non si interrompe se entry è vuoto


    def choose_res(self, choice):
        if choice not in ["Best", "Fast", "Fastest"]:
            self.res = self.yt_info[2][choice]
        else:
            self.res = choice



    def set_gui_on_change(self, choice):
        dbg.printfunc()
        for spec_GUI in self.gui.values():
            for widget in spec_GUI:
                if issubclass(widget.__class__, ctk.CTkBaseClass):
                    widget.place_forget()
                    widget.pack_forget()
        text = f"Use the {choice} tab as indicated"
        for widget in self.gui[choice]:
            if isinstance(widget, str):
                text = widget
            elif issubclass(widget.__class__, ctk.CTkBaseClass):
                if not widget.rel_pos:
                    widget.abs_place()
                else:
                    widget.rel_place()

            else:
                raise ValueError(f"Error: Widget {widget} class not fitting.")
        self.label.set_text(text)


    def print_text_size(self, text: str):
        dbg.printfunc()
        print(self.font.measure(text))

    def close(self):
        if (hasattr(self, "it") and self.it.is_alive()) or (hasattr(self, "thr") and self.thr.is_alive()):
            # ask widgets
            self.askframe = Frame(self, .5, .4, .6, .2, relative_position=True, relative_dimension=True, fg_color="#616161")
            self.askframe.rel_place() if self.askframe.rel_pos else self.askframe.abs_place()
            asklabel = Label(self.askframe, "You have processes in progress. Are you sure you want to close the app?", .5,
                             .25, relative_position=True, force_text=False, color="#000000")
            yes = Button(self.askframe, "YES", .25, .6, width=.4, height=.2, relative_position=True, relative_dimension=True,
                         color="#00aa00", command=lambda: self.choose(True), hover_color="#00d100")
            no = Button(self.askframe, "NO", .75, .6, width=.4, height=.2, relative_dimension=True, relative_position=True,
                        color="#aa0000", command=lambda: self.choose(False), hover_color="#d10000")
            set_font(self.askframe, self.font)
            asklabel.rel_place() if asklabel.rel_pos else asklabel.abs_place()
            yes.rel_place() if yes.rel_pos else yes.abs_place()
            no.rel_place() if no.rel_pos else no.abs_place()
        else:
            self.destroy()


    def choose(self, choice: bool):
        if choice:

            if hasattr(self, "it") and self.it.is_alive():
                self.it.stop()
            if hasattr(self, "thr") and self.thr.is_alive():
                self.thr.stop()
            # CHECK: close threads
            # self.after(2000, self.destroy)
            self.destroy()
        else:
            self.askframe.destroy()
            



if __name__ == "__main__":
    assert os.path.exists("..\\..\\utils\\ico\\download.ico")
    dbg.printdb("Started program")
    app = App()
    dbg.printdb("App done")
    app.mainloop()

# TODO: setup wizard
#  aggiungere:
#  sistema il popup di chiusura (magari con un'animazione)
#  il label generale deve cambiare a seconda degli errori
#  nel caso in cui il link del file finisca per .mp4 nella parte di download, basta fare un curl -o. non si possono ottenere le informazioni
#   o altro.
#  label dell'upgrade
#  CTRL + Z nelle labels, CTRL + Altro non fa eseguire il comando
#  Invio con file e link download (ma anche le cut entry). per il download del link, forzi subito l'avvio del
#   infothread, ma se il link non è valido lo segnali nel label generico.
#  aggiungi i requirements.text sia al python App, sia al python CLI
#  in una nuova versione, magari, aggiungi il modo di scaricare un video direttamente in clip
