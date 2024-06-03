"""import tkinter as tk
from tkinter import ttk


class CustomCombobox:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Custom Combobox")
        baseval = tk.StringVar()
        baseval.set("Select")
        style = ttk.Style()
        self.root.tk_setPalette("gray")
        style.theme_create('combostyle', parent='alt',
                                settings={'TCombobox':
                                              {'configure':
                                                   {'selectbackground': 'blue',
                                                    'fieldbackground': 'red',
                                                    'background': 'green'
                                                    }}})
        style.theme_use("combostyle")
        self.combobox = ttk.Combobox(root)

        # Set custom dropdown items
        self.custom_items = ["Python", "Java", "C++", "Other Language"]
        self.combobox['values'] = self.custom_items
        self.combobox["width"] = 100
        self.combobox["state"] = "readonly"

        # Bind a function to execute when an item is selected
        self.combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Pack the Combobox
        self.combobox.pack(pady=20)

    def on_combobox_select(self, event):
        selected_item = self.combobox.get()
        print(f"Selected item: {selected_item}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CustomCombobox(root)
    root.mainloop()



#come posso impostare un boolean nel mio file python che restituisce false se viene eseguito con python file.py



"""


import threading
import customtkinter
import yt_dlp


import customtkinter as ct
from moviepy.editor import VideoFileClip

class VideoTrimmer:
    def __init__(self, master):
        self.master = master
        self.progress_bar = ct.CTkProgressBar(master, width=200)
        self.progress_bar.pack()

    def trim_video(self, start_time, end_time):
        # Open the video file
        clip = VideoFileClip(self.video_file)

        # Trim the video
        trimmed_clip = clip.subclip(start_time, end_time)

        # Create a custom progress function
        def progress(frame):
            current_time = frame / clip.fps
            self.progress_bar.set(current_time / (end_time - start_time) * 100)
            self.master.update_idletasks()

        # Write the trimmed video to a new file
        trimmed_clip.write_videofile("trimmed_video.mp4", progress=progress)

        # Close the video file
        clip.close()
        trimmed_clip.close()


class DownloadThread(threading.Thread):
    def __init__(self, link, progress_bar, label, active_label):
        threading.Thread.__init__(self)
        self.link = link
        self.progress_bar = progress_bar
        self.label = label
        self.daemon = True
        self.active = active_label
    def run(self):
        ytdl_opts = {
            'progress_hooks': [self.my_hook],
            "format": "best",
            "prefer_player": "ios"
        }

        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([self.link])
        self.active.configure(text="DONE")
    def my_hook(self, d):
        if d['status'] == 'downloading':

            self.progress_bar.set(float(d['_percent_str'].strip('%'))/100)
            self.label.configure(text=f"Downloading... {d['_percent_str']}  ETA: {d['_eta_str']}")

# Create your customtkinter window and progress bar
root = customtkinter.CTk()
root.geometry("400x100")
progress_bar = customtkinter.CTkProgressBar(root, width=300)
label = customtkinter.CTkLabel(root, text="")
progress_bar.pack(pady=20)
label.pack()
progress_bar.set(0)

active_label = customtkinter.CTkLabel(root, text="")
active_label.pack()
# Start the download thread
thread = DownloadThread("https://www.youtube.com/watch?v=dQw4w9WgXcQ", progress_bar, label, active_label)
thread.start()
# Start the main loop
try:
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()