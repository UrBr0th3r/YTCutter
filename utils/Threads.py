from moviepy.editor import VideoFileClip
from proglog import ProgressBarLogger
from time import time, sleep

import sys
import threading
import json
import subprocess
import time
from utils.Utils import *
from tkinter import messagebox
import os
import psutil
import re

yt_dlp_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "yt-dlp.exe")
ffmpeg_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg.exe")

if not os.path.exists(yt_dlp_loc) or not os.path.exists(ffmpeg_loc):
    messagebox.showerror("ALERT", "Can't find all executable files!\nPlease, check if bin dir is on your utils directory")
    sys.exit(1)

class InfoThread(threading.Thread):
    title: str
    resolutions: dict[str, str]
    duration: str
    app = None
    option_select = None
    def __init__(self, link:str, app = None, option_select = None, icon_text = None):
        super().__init__()
        self.newlink = link
        self.icon_text = icon_text
        #self.daemon = True
        self.running = True
        if app:
            self.app = app
            self.option_select = option_select
    def run(self):
        self.get_info()

    def get_info(self):
        if self.app:
            self.option_select.set("Loading")
            self.option_select.configure(values=[])
            self.icon_text.configure(text_color="gray")
            self.icon_text.set_text("O")
            self.app.download_button.configure(state="disabled", fg_color="gray")
            # SET ICON LOADING
        command = f"{yt_dlp_loc} --dump-json {self.newlink}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True)
        stdout, stderr = self.proc.communicate()
        # CANARY
        if self.app.canary:
            if stderr:
                self.icon_text.configure(text_color="red")
                self.icon_text.set_text("X")
                #print(f"Errori:\n{stderr}")
            else:
                self.icon_text.configure(text_color="green")
                self.icon_text.set_text("✓")
                js = json.loads(stdout)
                self.title = js.get("title", None).replace(" ", "_").translate(str.maketrans("","", string.punctuation.replace("_", "")))+".mp4"
                self.resolutions = {f.get("resolution"): f.get("format_id") for f in js.get("formats", []) if f["ext"] == "mp4"}
                if ("audio only" in self.resolutions.keys()):
                    self.resolutions.pop("audio only")
                self.duration = str(float(js.get("duration")))
                if self.app:
                    self.app.yt_info = [self.title, self.duration, self.resolutions]
                    self.option_select.set("Resolution")
                    self.option_select.configure(values=list(self.resolutions.keys())+["Best","Fast","Fastest"])
                    self.app.download_button.configure(state="normal", fg_color=self.app.cut_button.cget("fg_color"))
    def changelink(self, link):
        print("Changed link to "+link)
        self.newlink = link
    def stop(self):
        try:
            proc_id = psutil.Process(self.proc.pid)
            for proc in proc_id.children(recursive=True):
                proc.terminate()
            proc_id.terminate()
        except psutil.NoSuchProcess:
            pass

class DownloadThread(threading.Thread):

    perc: float
    eta: str
    app = None
    progress_bar = None
    label = None
    def __init__(self, link: str, output_loc: str, quality: str, total_duration: str, app = None, progress_bar = None, label = None):
        super().__init__()
        if "&" in link:
            link = get_text(link, (None, "&"))
        self.link = link
        self.output_loc = output_loc
        self.quality = quality
        self.duration = total_duration
        self.daemon = True
        self.video_out = r".\video_tmp.webm"
        self.audio_out = r".\audio_tmp.m4a"
        if app:
            self.app = app
            self.progress_bar = progress_bar
            self.label = label
    def run(self):
        try:
            if self.app:
                self.progress_bar.set(0)
                self.progress_bar.abs_place() if not self.progress_bar.rel_pos else self.progress_bar.rel_place()
                self.label.set_text("Starting download ...")
                self.label.abs_place() if not self.label.rel_pos else self.label.rel_place()

            #print("RUN")
            #print(self.quality)
            if self.quality != "Fast" and self.quality != "Fastest":
                #print("Quality !")
                self.download(self.quality)
                self.download("audio")
                self.merge(self.video_out, self.audio_out)
            else:
                #print("Quality")
                self.fastdownload(self.quality)
            print(f"Video downloaded in {self.output_loc}")
            if self.app:
                self.progress_bar.set(1)
                self.label.set_text(f"Video downloaded in {self.output_loc}")
        except Exception as e:
            print(e)
    def download(self, mode: str):
        #print(f"Starting {mode}")
        command = f"{yt_dlp_loc} {self.link} -o {self.audio_out if mode == "audio" else self.video_out} -f {"bestaudio[ext=m4a]" if mode == "audio" else "bestvideo[ext=mp4]" if mode == "Best" else self.quality}".split()
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)

        start_time = time.time_ns()
        print(f"Starting download {mode}")
        while True:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                break
            if "ERROR" in output:
                print(output)
                if self.app:
                    self.progress_bar.set(0)
                    self.label.set_text(text=output)
                    break
            if output:
                if "%" in output.strip():
                    #print(output.strip())
                    self.perc = float(get_text(output.strip(), ("[download]", "%")))
                    #speed = get_text(output.strip(), ("at", "ETA"))

                    ns = time.time_ns() - start_time
                    etat = (ns*100/(self.perc if self.perc != 0 else 0.05) - ns)/1e9
                    #print(etat)
                    etaT = Time(str(etat), "S.F")
                    self.eta = etaT.classic()

                    print(f"\rDownloading {"audio" if mode == "audio" else "video"}... {self.perc}%  ETA: {self.eta}", end="")
                    if self.app:
                        self.progress_bar.set(self.perc / 200 + 0.5 * (1 if mode == "audio" else 0))
                        self.label.set_text(text=f"Downloading {"audio" if mode == "audio" else "video"}... {self.perc}%  ETA: {self.eta}")


        proc.wait()
        print(f"\nDone downloading {mode}")
    def merge(self, video_loc:str, audio_loc:str):
        command = f"{ffmpeg_loc} -i {video_loc} -i {audio_loc} {self.output_loc} -c:v copy -c:a copy -qscale 0 -y"  # .split()
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("Start merging")
        start_time = time.time_ns()
        output = proc.stdout
        for line in output:
            if "time=" in line:
                done = get_text(line, ("time=", "bitrate"))
                total = self.duration
                doneT = Time(done, "hh:mm:ss.F")
                totalT = Time(total, "S.F")
                dones = doneT.in_secs()
                totals = totalT.in_secs()
                self.perc = round((dones * 100 / totals), 2)
                if self.perc < 0:
                    self.perc = 0.0
                if self.perc > 100:
                    self.perc = 100
                ns = time.time_ns() - start_time
                etat = (ns * 100 / (self.perc if self.perc != 0 else 0.05) - ns) / 1e9
                if etat < 0:
                    etat = 0.0
                try:
                    etaT = Time((str(etat) if etat > 0 else "0.0"), "S.F")
                except ValueError:
                    etaT = Time("0", "S")
                self.eta = etaT.classic()
                print(f"\rMerging... {self.perc}%  ETA: {self.eta}", end="")
                if self.app:
                    self.progress_bar.set(self.perc / 100)
                    self.label.set_text(text=f"Merging... {self.perc}%  ETA: {self.eta}")

        # proc.wait()

        # stdout, stderr = proc.communicate()
        # print(stdout, stderr)
        os.remove(video_loc)
        os.remove(audio_loc)
        print("\nDone merging")
    def fastdownload(self, quality):
        command = f"{yt_dlp_loc} {self.link} -o {self.output_loc} -f {"best[ext=mp4]" if quality == "Fast" else "worst[ext=mp4]"}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
        start_time = time.time_ns()
        print(f"Starting fast download")
        while True:
            output = self.proc.stdout.readline()
            if output == '' and self.proc.poll() is not None:
                break
            if output:
                if "%" in output.strip():
                    # print(output.strip())
                    self.perc = float(get_text(output.strip(), ("[download]", "%")))

                    ns = time.time_ns() - start_time
                    etat = (ns * 100 / (self.perc if self.perc != 0 else 0.05) - ns) / 1e9
                    # print(etat)
                    etaT = Time(str(etat), "S.F")
                    self.eta = etaT.classic()

                    print(f"\rDownloading video... {self.perc}%  ETA: {self.eta}", end="")
                    if self.app:
                        self.progress_bar.set(self.perc / 100)
                        self.label.set_text(text=f"Downloading video... {self.perc}%  ETA: {self.eta}")
    def stop(self):
        try:
            proc_id = psutil.Process(self.proc.pid)
            for proc in proc_id.children(recursive=True):
                proc.terminate()
            proc_id.terminate()
        except psutil.NoSuchProcess:
            pass


class MyBarLogger(ProgressBarLogger):
    def __init__(self, app, progress_var, label_var):
        super().__init__()
        self.app = app
        self.progress_var = progress_var
        self.label_var = label_var
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
    def __init__(self, app, progbar, label, video_file: str, ranges: list[tuple[str, str]]):
        super().__init__()

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
        for rowN in range(self.master.row+1):
            try:
                self.master.remove_widgets(self.master.scrollframe, rowN)
            except IndexError:
                pass
        self.master.add_widget()

    @classmethod
    def parse_time(cls, time_piece):

        pattern = re.compile(r'^(?:(\d{1,2}):)?(?:(\d{1,2}):)?(\d{1,2})(\.\d+)?$')
        match = pattern.match(time_piece)
        if match:
            hours = match.group(1)
            minutes = match.group(2)
            seconds = match.group(3)
            ms = match.group(4)
            if hours and not minutes:
                minutes = hours
                hours = None
            time_tot:float = 0.0
            time_tot += float(seconds) if seconds else 0
            time_tot += float(minutes)*60 if minutes else 0
            time_tot += float(hours)*3600 if hours else 0
            time_tot += float(ms) if ms else 0
        else:
            raise ValueError(f"Bad parse in {time_piece}. Hover over cut entries to know more about parsing model")
        return time_tot


    def trim_video(self, start_ins: str | None, end_ins: str | None, idx: int):
        # TODO: block all widgets while cutting
        self.logger.update_time(time())
        self.logger.update_idx(idx)
        # Open the video file
        clip = VideoFileClip(self.video_file)
        start_time: float
        end_time: float
        try:
            start_time = 0.0 if not start_ins else self.parse_time(start_ins)

            end_time = clip.duration if not end_ins else self.parse_time(end_ins)

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




class TryThread(threading.Thread):
    def run(self):
        for i in range(100):
            print("CIAO")
            time.sleep(.5)








if __name__ == "__main__":
    """info = InfoThread("https://www.youtube.com/watch?v=PA07y")
    info.start()"""

    """dwl = DownloadThread("https://www.youtube.com/watch?v=3_X_Hd1XpXE", ".\\boh.mp4", "603", "1141.0")
    dwl.start()
    dwl.join()"""

    print(VideoTrimmer.parse_time("22:1.45"))
    # TODO: cambia Utils.Time con delle regex

    # print(dt.title)





