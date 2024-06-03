import customtkinter as ctk
from typing import Callable, Union
import ctypes
from abc import ABC,abstractmethod
import threading
import yt_dlp

class DownloadThread(threading.Thread):
    def __init__(self, link, progress_bar, label):
        threading.Thread.__init__(self)
        self.link = link
        self.progress_bar = progress_bar
        self.label = label
        self.daemon = True

    def run(self):
        ytdl_opts = {
            'progress_hooks': [self.my_hook],
            "format": "best",
            "prefer_player": "ios"
        }
        self.progress_bar.abs_place() if not self.progress_bar.rel_pos else self.progress_bar.rel_place()
        self.label.abs_place() if not self.label.rel_pos else self.label.rel_place()
        self.progress_bar.set(0)
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([self.link])

    def my_hook(self, d):
        if d['status'] == 'downloading':

            self.progress_bar.set(float(d['_percent_str'].strip('%'))/100)
            self.label.configure(text=f"Downloading... {d['_percent_str']}  ETA: {d['_eta_str']}")


class Methods(ABC, ctk.CTkBaseClass):
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
    @abstractmethod
    def base_command(self, entry):
        pass


def is_running_in_console():
    try:
        kernel32 = ctypes.windll.kernel32
        # Get the console window handle
        console_handle = kernel32.GetConsoleWindow()
        if console_handle != 0:
            return True
        else:
            return False
    except Exception as e:
        return False


class Label(ctk.CTkLabel, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, text:str, x:float, y:float, *,  width:float = 0, height:float = 0, color: str = None, relative_position: bool = False, relative_dimension: bool = False):
        super().__init__(app, text=text)
        self.x = x
        self.y = y
        self.rel_pos = relative_position
        if color is not None:
            self.configure(fg_color=color)
        if relative_dimension:
            width *= app.dim[0]
            height *= app.dim[1]
        if width != 0:
            self.configure(width=width)
        if height != 0:
            self.configure(height=height)

class ProgressBar(ctk.CTkProgressBar, Methods):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, x:float, y:float, *, width:float = 0, height:float =0, color: str = None, relative_position: bool = False, relative_dimension: bool = False, starting_point:float = 0):
        super().__init__(app)
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

class Button(ctk.CTkButton, Methods):
    x:float
    y:float
    text:str
    rel_pos: bool
    grid_pos: bool
    extracted: str = None
    def __init__(self, app, text: str, x:float, y:float, *args, width:float = 0, height:float = 0, color: str = None, command: Callable = None, relative_position: bool = False, relative_dimension: bool = False, grid_position: bool = False):
        super().__init__(app, text=text, *args)
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

    def extract(self, entry):
        self.extracted = entry.get()
        print(f"{self.text}: self.extracted set to {self.extracted}")


class OptionMenu(Methods, ctk.CTkOptionMenu):
    width:int = 200
    x:float
    y:float
    rel_pos:bool
    def __init__(self, app, values:list[str], x:float, y:float, color:str = None, command:Callable = None, *, relative_position:bool = False):
        super().__init__(app, values=values, width=self.width)
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

class Entry(Methods, ctk.CTkEntry):
    x: float
    y: float
    rel_pos: bool
    def __init__(self, app, x: float, y:float, *args, width: float = 0, height: float = 0, bg_text: str = None, color: str = None, relative_position:bool = False, relative_dimension: bool = False):
        super().__init__(app, *args)
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

class App(ctk.CTk):
    font: ctk.CTkFont
    gui: dict[str, list[Union[Methods, Button, Entry]]]
    dim: tuple[int, int]
    font: ctk.CTkFont = None
    def __init__(self, dim: tuple[int, int], title: str, *, font: tuple[str, int] = None):
        super().__init__()
        self.dim = dim
        self.geometry(f"{dim[0]}x{dim[1]}")
        self.title(title)

        ctk.set_default_color_theme("green")

        # download gui
        self.link_entry = Entry(self, 0.4, 0.35, width=0.6, height=0.1, relative_position=True, relative_dimension=True, bg_text="Enter YouTube link...")
        self.download_button = Button(self, "Download", 0.8, 0.35, height=0.1, relative_dimension=True, relative_position=True)
        self.download_button.configure(command=lambda: self.download_button.extract(self.link_entry))

        # file gui
        self.file_entry = Entry(self, 0.4, 0.35, width=0.6, height=0.1, relative_position=True, relative_dimension=True, bg_text="Enter local video file...")
        self.check_button = Button(self, "Check", 0.8, 0.35, height=0.1, relative_dimension=True, relative_position=True)
        self.check_button.configure(command= lambda: self.check_button.extract(self.file_entry))

        # range gui: start end -> blank; progress bar will be a sum of 2 progress bar, both initialized like in trash.py


        self.gui = {
            "Download" : [
                self.link_entry,
                self.download_button

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

        if font is not None:
            self.set_font(self, font)

        """download_bool: bool = False
        while not download_bool:
            if self.download_button.extracted is not None:
                print(f"Found: {self.download_button.extracted}")
                download_bool = True"""
        return


    def set_font(self, parent, font: tuple[str, int]):
        f = ctk.CTkFont(font[0], font[1])
        self.font = f
        for widget in parent.winfo_children():
            try:
                widget.set_font(self.font)
            except Exception as e:
                print(f"Cannot set font for {widget}: {e}")

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



if __name__ == "__main__":
    app = App((600, 500), "CTK", font=("Arial", 20))
    print("App done")
    app.mainloop()


    # TODO: a quanto pare app.mainloop blocca tutto, quindi bisogna importare tutto in un def dell'app, prima aggiusta tutto