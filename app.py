print("Script started")
from PIL import Image, ImageTk
import customtkinter as ctk
from customtkinter import filedialog as fd
from typing import Callable, Union
from abc import ABC
import math

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import string, inspect

from moviepy.editor import VideoFileClip
from proglog import ProgressBarLogger
from time import time, sleep
from datetime import datetime

import sys
import threading
import json
import subprocess
import time
from tkinter import messagebox
import os

import re

yt_dlp_loc = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "bin", "yt-dlp.exe")
print(yt_dlp_loc)
ffmpeg_loc = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "bin", "ffmpeg.exe")
ico_loc = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))),"utils", "ico", "download.ico")

EXTENSIONS = ("3g2", "3gp", "a64", "ac3", "ac4", "adts", "adx", "aea", "aiff", "alaw", "alp", "amr", "amv", "apm", "apng", "aptx", "aptx_hd", "argo_asf", "argo_cvg", "asf", "asf_stream", "ass", "ast", "au", "avi", "avif", "avm2", "avs2", "avs3", "bit", "d caca", "caf", "cavsvideo", "chromaprint", "codec2", "codec2raw", "crc", "dash", "data", "daud", "dfpwm", "dirac", "dnxhd", "dts", "dv", "dvd", "eac3", "evc", "f32be", "f32le", "f4v", "f64be", "f64le", "ffmetadata", "fifo", "film_cpk", "filmstrip", "fits", "flac", "flv", "framecrc", "framehash", "framemd5", "g722", "g723_1", "g726", "g726le", "gif", "gsm", "gxf", "h261", "h263", "h264", "hash", "hds", "hevc", "hls", "iamf", "ico", "ilbc", "image2", "image2pipe", "ipod", "ircam", "ismv", "ivf", "jacosub", "kvag", "latm", "lc3", "lrc", "m4v", "matroska", "md5", "microdvd", "mjpeg", "mlp", "mmf", "mov", "mp2", "mp3", "mp4", "mpeg", "mpeg1video", "mpeg2video", "mpegts", "mpjpeg", "mulaw", "mxf", "mxf_d10", "mxf_opatom", "null", "nut", "obu", "oga", "ogg", "ogv", "oma", "opus", "psp", "rawvideo", "rcwt", "rm", "roq", "rso", "rtp", "rtp_mpegts", "rtsp", "s16be", "s16le", "s24be", "s24le", "s32be", "s32le", "s8", "sap", "sbc", "scc", "d sdl", "sdl2", "segment", "smjpeg", "sox", "spdif", "spx", "srt", "streamhash", "sup", "svcd", "swf", "tee", "truehd", "tta", "ttml", "u16be", "u16le", "u24be", "u24le", "u32be", "u32le", "u8", "vc1", "vc1test", "vcd", "vidc", "vob", "voc", "vvc", "w64", "wav", "webm", "webm_chunk", "webp", "webvtt", "wsaud", "wtv", "wv", "yuv4mpegpipe")
if not os.path.exists(yt_dlp_loc) or not os.path.exists(ffmpeg_loc):
    print("Cant find executable files")
    messagebox.showerror("ALERT", "Can't find all executable files!\nPlease, check if bin dir is on your utils directory")
    sys.exit(1)

class InfoThread(threading.Thread):
    title: str
    resolutions: dict[str, str]
    duration: str | None
    app = None
    option_select = None
    def __init__(self, link:str, app = None, option_select = None, icon_text = None):
        super().__init__()
        self.newlink = link
        self.icon_text = icon_text
        self.daemon = True
        self.running = True
        if app:
            self.app = app
            self.option_select = option_select
        self.stop_bool = False
    def run(self):
        self.get_info()

    def get_info(self):
        print("Getting info")
        if self.app:
            self.option_select.set("Loading")
            self.option_select.configure(values=[])
            self.icon_text.configure(text_color="gray")
            self.icon_text.set_text("O")
            self.app.download_button.configure(state="disabled", fg_color="gray")
        command = f"{yt_dlp_loc} --dump-json {self.newlink}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True)
        print(f"process done. alive: {self.proc.poll()}")
        stdout, stderr = self.proc.communicate()
        print(self.newlink, self.stop_bool)
        if not self.stop_bool:
            # CANARY
            if stderr and any("ERROR" in errs for errs in stderr.split("\n")):
                if self.app:
                    self.icon_text.configure(text_color="red")
                    self.icon_text.set_text("X")
                    self.app.label.set_text(f"Error: {get_text(stderr, (']', '.'))}")
                print(f"Errors:\n{stderr}")
            else:
                try:
                    js = json.loads(stdout)
                except json.decoder.JSONDecodeError as e:
                    self.icon_text.configure(text_color="red")
                    self.icon_text.set_text("X")
                    self.app.label.set_text("Error in loading infos")
                else:
                    if self.app:
                        self.icon_text.configure(text_color="green")
                        self.icon_text.set_text("✓")
                        self.app.label.set_text("URL exists and it is accessible")
                    self.title = js.get("title", "downloaded_video").replace(" ", "_").translate(str.maketrans("","", string.punctuation.replace("_", "")))+".mp4"
                    self.resolutions = {"Fixed":"Fixed"} if any(el.endswith(f".{ext}") for el in self.newlink.split("&") for ext in EXTENSIONS) else {f.get("resolution"): f.get("format_id") for f in js.get("formats", []) if f["ext"] == "mp4"}

                    if ("audio only" in self.resolutions.keys()):
                        self.resolutions.pop("audio only")
                    try:
                        self.duration = str(float(js.get("duration")))
                    except (TypeError, ValueError):
                        self.duration = None
                    print(self.title, self.resolutions, self.duration)
                    if self.app:
                        self.app.yt_info = [self.title, self.duration, self.resolutions]
                        if "Fixed" in self.resolutions.keys():
                            self.option_select.set("Fixed")
                        else:
                            self.option_select.set("Resolution")
                            self.option_select.configure(values=list(self.resolutions.keys())+["Best","Fast","Fastest"])
                        self.app.download_button.configure(state="normal", fg_color=self.app.cut_button.cget("fg_color"))
                        if self.option_select.dinamic_width:
                            self.option_select.set_dinamic_width(list(self.resolutions.keys())+["Best","Fast","Fastest"])

    def changelink(self, link):
        print("Changed link to "+link)
        self.newlink = link
    def stop(self):
        try:
            self.proc.kill()
        except AttributeError as e:
            print(e)
        self.stop_bool = True

        # CHECK: non continua più?, ERROR: il processo continua per qualche motivo, ma almeno stop_bool è true
        #  quindi dovrebbe effettivamente non influire (va ad influire però sul processore)

class FileInfoThread(threading.Thread):
    def __init__(self, fileloc: str, app = None, icon_text = None):
        super().__init__()
        self.fileloc = fileloc
        self.app = app
        self.icon_text = icon_text
        self.stop_bool = False
        self.daemon = True
    def run(self):
        if not self.stop_bool:
            if os.path.exists(self.fileloc) and os.path.isfile(self.fileloc) and self.fileloc[self.fileloc.rindex(".")+1:] in EXTENSIONS:
                if self.app:
                    self.icon_text.configure(text_color="green")
                    self.icon_text.set_text("✓")
                    self.app.label.set_text("File exists")
                    self.app.file_loc = self.fileloc
                else:
                    print("Exists")
                    # CHECK
            else:
                if self.app:
                    self.icon_text.configure(text_color="red")
                    self.icon_text.set_text("X")
                    self.app.label.set_text("File does not exists" if self.fileloc[self.fileloc.rindex(".")+1:] in EXTENSIONS else "File with wrong extension")
                else:
                    print("Doesnt exists")
                    # CHECK

    def stop(self):
        self.stop_bool = True

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
        self.stop_bool = False
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
                self.app.download_button.configure(state="disabled", fg_color="gray")
                self.label.abs_place() if not self.label.rel_pos else self.label.rel_place()

            #print("RUN")
            #print(self.quality)
            if self.quality != "Fast" and self.quality != "Fastest" and self.quality != "Fixed":
                #print("Quality !")
                self.download(self.quality)
                self.download("audio")
                self.merge(self.video_out, self.audio_out)
            else:
                #print("Quality")
                self.fastdownload(self.quality)
            if not self.stop_bool:
                print(f"Video downloaded in {self.output_loc}")
                if self.app:
                    self.app.file_loc = self.output_loc
                    self.app.duration = self.duration
                    self.progress_bar.set(1)
                    self.label.set_text(f"Video downloaded in {self.output_loc}")
                    self.app.download_button.configure(state="normal", fg_color=self.app.cut_button.cget("fg_color"))
                os.utime(self.output_loc, (datetime.now().timestamp(), datetime.now().timestamp()))

        except Exception as e:
            print("\nERROR: "+str(e))
            self.app.download_button.configure(state="normal", fg_color=self.app.cut_button.cget("fg_color"))
    def download(self, mode: str):
        #print(f"Starting {mode}")
        command = f"{yt_dlp_loc} {self.link} -o {self.audio_out if mode == 'audio' else self.video_out} -f {'bestaudio[ext=m4a]' if mode == 'audio' else 'bestvideo[ext=mp4]' if mode == 'Best' else self.quality}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)

        start_time = time.time_ns()
        print(f"Starting download {'audio' if mode == 'audio' else 'video'}")
        while True:
            output = self.proc.stdout.readline()
            if (output == '' and self.proc.poll() is not None) or self.stop_bool:
                break
            if "ERROR" in output:
                if self.app:
                    self.progress_bar.set(0)
                    self.label.set_text(output)
                raise ConnectionRefusedError(output)
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

                    print(f"\rDownloading {'audio' if mode == 'audio' else 'video'}... {self.perc}%  ETA: {self.eta}", end="")
                    if self.app:
                        self.progress_bar.set(self.perc / 200 + 0.5 * (1 if mode == "audio" else 0))
                        self.label.set_text(f"Downloading {'audio' if mode == 'audio' else 'video'}... {self.perc}%  ETA: {self.eta}")


        #self.proc.wait()
        if not self.stop_bool:
            print(f"\nDone downloading {mode}")
    def merge(self, video_loc:str, audio_loc:str):
        command = f"{ffmpeg_loc} -i {video_loc} -i {audio_loc} -c:v copy -c:a copy -qscale 0 -y {self.output_loc}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("Start merging")
        start_time = time.time_ns()
        output = self.proc.stdout
        if not self.stop_bool:
            for line in output:
                if "time=" in line:
                    if self.duration:
                        done = get_text(line, ("time=", "bitrate"))
                        total = self.duration
                        try:
                            doneT = Time(done, "hh:mm:ss.F")
                            totalT = Time(total, "S.F")
                        except ValueError:
                            doneT = Time("1", "s")
                            totalT = Time("1", "s")
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
                    else:
                        self.eta = "Unknown"
                    print(f"\rMerging... {self.perc}%  ETA: {self.eta}", end="")
                    if self.app:
                        self.progress_bar.set(self.perc / 100)
                        self.label.set_text(f"Merging... {self.perc}%  ETA: {self.eta}")

        # proc.wait()

        # stdout, stderr = proc.communicate()
        # print(stdout, stderr)
        if not self.stop_bool:
            os.remove(video_loc)
            os.remove(audio_loc)
            print("\nDone merging")
    def fastdownload(self, quality):
        if quality != "Fixed":
            command = f"{yt_dlp_loc} {self.link} -o {self.output_loc} -f {'best[ext=mp4]' if quality == 'Fast' else 'worst[ext=mp4]'}".split()
        else:
            command = f"{yt_dlp_loc} {self.link} -o {self.output_loc}".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)
        start_time = time.time_ns()
        print(f"Starting fast download")
        print(' '.join(command))

        while True:
            output = self.proc.stdout.readline()
            if (output == '' and self.proc.poll() is not None) or self.stop_bool:
                break
            if "ERROR" in output:
                if self.app:
                    self.progress_bar.set(0)
                    self.label.set_text(output)
                raise ConnectionRefusedError(f"{output}")
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
                        self.label.set_text(f"Downloading video... {self.perc}%  ETA: {self.eta}")
        if not self.stop_bool:
            print("\nDone fast downloading")


    def stop(self):
        try:
            self.proc.kill()
        except AttributeError:
            pass
        self.stop_bool = True



class MyBarLogger:
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

    def bars_callback(self, percentage, ETA, old_value=None):
        if 'Writing video' in self.last_message:
            if percentage > 0 and percentage <= 100:
                if int(percentage) != self.previous_percentage:
                    ETAs = round((time.time()-self.time)*(100-percentage)/percentage)
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
        self.master.download_button.configure(state="disabled", fg_color="gray")
        self.master.cut_button.configure(state="disabled", fg_color="gray")
        for rngIdx in range(len(self.range_values)):

            self.trim_video(self.range_values[rngIdx][0], self.range_values[rngIdx][1], rngIdx)
            sleep(.5)
        for rowN in range(self.master.row+1):
            try:
                self.master.remove_widgets(self.master.scrollframe, rowN)
            except IndexError:
                pass
        self.master.add_widget()
        self.master.download_button.configure(state="normal", fg_color=self.master.check_button.cget("fg_color"))
        self.master.cut_button.configure(state="normal", fg_color=self.master.check_button.cget("fg_color"))

    @classmethod
    def parse_time(cls, time_piece):

        pattern = re.compile(r'^(?:(\d+):)?(?:(\d+):)?(\d+)(\.\d+)?$')
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
        """
        command = f"{ffmpeg_loc} -i {video_loc} -i {audio_loc} {self.output_loc} -c:v copy -c:a copy -qscale 0 -y".split()
        self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        print("Start merging")
        start_time = time.time_ns()
        output = self.proc.stdout
        if not self.stop_bool:
            for line in output:
                if "time=" in line:
                    if self.duration:
                        done = get_text(line, ("time=", "bitrate"))
                        total = self.duration
                        try:
                            doneT = Time(done, "hh:mm:ss.F")
                            totalT = Time(total, "S.F")
                        except ValueError:
                            doneT = Time("1", "s")
                            totalT = Time("1", "s")
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
                    else:
                        self.eta = "Unknown"
                    print(f"\rMerging... {self.perc}%  ETA: {self.eta}", end="")
                    if self.app:
                        self.progress_bar.set(self.perc / 100)
                        self.label.set_text(text=f"Merging... {self.perc}%  ETA: {self.eta}")

        # proc.wait()

        # stdout, stderr = proc.communicate()
        # print(stdout, stderr)
        if not self.stop_bool:
            os.remove(video_loc)
            os.remove(audio_loc)
            print("\nDone merging")
        """
        # DOING: cambia VideoFileClip con ffmpeg
        self.logger.update_time(time.time())
        self.logger.update_idx(idx)
        # Open the video file
        # clip = VideoFileClip(self.video_file)
        start_time: float
        end_time: float
        try:
            start_time = 0.0 if not start_ins else self.parse_time(start_ins)

            end_time = Time(self.master.duration, "S.F").in_secs() if not end_ins else self.parse_time(end_ins)

            if start_time >= end_time:
                raise ValueError("Start time is bigger than end time")


            # Trim the video
            if start_ins and end_ins:
                #trimmed_clip = clip.subclip(start_time, end_time)
                # fai partire il comando dal Popen
                # Write the trimmed video to a new file
                title = self.video_file[:self.video_file.rindex(".mp4")]+f"_[{start_ins.replace(':','.') if start_ins else 'Start'}-{end_ins.replace(':','.') if end_ins else 'End'}].mp4"

                self.logger.update_name(title)
                self.label.set_text("Starting to cut...")
                # DOING: aggiungi il comando con il Popen e prendi dallo STDOUT il tempo e parsalo
                self.label.rel_place() if self.label.rel_pos else self.label.abs_place()
                self.progress_bar.set(0)
                self.progress_bar.rel_place() if self.progress_bar.rel_pos else self.progress_bar.abs_place()
                command = f"{ffmpeg_loc} -i -ss {start_time} -to {end_time} {self.video_file} -c copy -qscale 0 -avoid_negative_ts 1 -y {title}".split(" ")
                #trimmed_clip.write_videofile(title, logger=self.logger)

                # Close the video file
                #trimmed_clip.close()
                self.label.set_text(f"Cut #{idx + 1} saved in: {title}")

                #self.label.set_text(f"Cut #{idx+1}: Saved in {title}")
        except ValueError as e:
            self.label.set_text(f"Error: {str(e)}")
            self.label.rel_place() if self.label.rel_pos else self.label.abs_place()
        finally:
            # clip.close()




class TryThread(threading.Thread):
    def run(self):
        for i in range(100):
            print("CIAO")
            time.sleep(.5)







def get_text(phrase: str, to_search: tuple[str | None, str | None]):
    try:
        stidx = phrase.index(to_search[0]) + len(to_search[0]) if to_search[0] else 0
    except ValueError:
        stidx = 0
    try:
        enidx = phrase.index(to_search[1]) if to_search[1] else len(phrase)
    except ValueError:
        enidx = len(phrase)
    return phrase[stidx: enidx].strip(" ")


class Time:
    def __init__(self, time: str, format: str):
        """
        Gets info according to format parameter
        :param time: Time to format
        :param format: letters: h, m, s, f (0.f secs). use uppercase to automatically count cyphers between symbols
        :return: Returns
        """
        if any(f not in "hmsfHMSF" + string.punctuation.replace("(", "").replace(")", "") for f in format):
            raise ValueError("Bad format")
        pattern = (format
                   .replace("h", r"(\d)")
                   .replace("m", r"(\d)")
                   .replace("s", r"(\d)")
                   .replace("f", r"(\d)")
                   .replace("H", r"(\d+)")
                   .replace("M", r"(\d+)")
                   .replace("S", r"(\d+)")
                   .replace("F", r"(\d+)")
                   )
        """pattern = "("+pattern+")"
        for i in range(len(pattern)):
            if pattern[i] in string.punctuation:
                pattern = pattern[:i]+")"+pattern[i]+"("+pattern[i+1:]
        """
        time_idxs: dict[str, list[int]] = {}
        gcount = 1
        for char in format:
            if char in "hmsfHMSF":
                try:
                    time_idxs[char].append(gcount)
                except KeyError:
                    time_idxs[char] = []
                    time_idxs[char].append(gcount)
                gcount += 1

        match = re.match(pattern, time)

        if not match:
            raise ValueError(f"Bad time (or format). With pattern: {pattern}, you searched in {time}")

        self.hour = ""
        self.minutes = ""
        self.seconds = ""
        self.fsecs = ""

        try:
            for idx in time_idxs["h"]:
                self.hour += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["m"]:
                self.minutes += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["s"]:
                self.seconds += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["f"]:
                self.fsecs += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["H"]:
                self.hour += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["M"]:
                self.minutes += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["S"]:
                self.seconds += match.group(idx)
        except KeyError:
            pass
        try:
            for idx in time_idxs["F"]:
                self.fsecs += match.group(idx)
        except KeyError:
            pass
        self.hour = int(self.hour if self.hour != "" else 0)
        self.minutes = int(self.minutes if self.minutes != "" else 0)
        self.seconds = int(self.seconds if self.seconds != "" else 0)
        self.fsecs = int(self.fsecs) if self.fsecs != "" else 0
        self.minutes += self.seconds // 60
        self.seconds %= 60
        self.hour += self.minutes // 60
        self.minutes %= 60

    def in_format(self, format):
        """
        Formats time according to format parameter
        :param format: letters: h, m, s, f (0.f secs). use uppercase to automatically count cyphers between symbols. if cypers are less than actual, the ones left will not be used. if + is used before the character, that means that every "upper" value will be added to that
        :return: string of time formatted
        """
        time_idxs: dict[str, list[list[int] | bool]] = {}
        for idx in range(len(format)):
            if format[idx] in "hmsfHMSF":
                try:
                    time_idxs[format[idx]][0].append(idx)
                except KeyError or NameError or UnboundLocalError:
                    time_idxs[format[idx]] = [[], False]
                    time_idxs[format[idx]][0].append(idx)
            if format[idx] == "+":
                time_idxs[format[idx + 1]][1] = True
        raise NotImplementedError("BRUH")
        # TODO: prendi gli indici e mettici gli indici dei valori

    def classic(self) -> str:
        return f"{f'{self.hour:02}:' if self.hour != 0 else ''}{f'{self.minutes:02}:' if self.minutes != 0 else ('00:' if self.hour != 0 else '')}{f'{self.seconds:02}' if self.seconds != 0 else '00'}.{round(self.fsecs / pow(10, len(str(self.fsecs)) - 3)) if self.fsecs != 0 else '0'}"

    def in_secs(self) -> float:
        return self.hour * 3600 + self.minutes * 60 + self.seconds + self.fsecs / pow(10, len(str(self.fsecs)))


class Debugger:
    debug: bool

    def __init__(self, debug: bool):
        self.debug = debug

    def printfunc(self):
        if self.debug:
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            args, _, _, values = inspect.getargvalues(frame)
            print(f"Entered function: {func_name if func_name != '__init__' else 'defined class'}. Args: " + (
                ' | '.join(f"{arg} = {values[arg]}" for arg in args)))

    def printdb(self, to_print: str):
        if self.debug:
            print(to_print)


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

    def set_text(self, divtext):
        """new_font = ctk.CTkFont(app.font.cget("family"), get_maximum_font_dim(self.wrap, 0, text, app.font))
        self.configure(font=new_font)"""
        dbg.printfunc()
        new_font = self.app.font
        nl = []
        for text in divtext.split("\n"):
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
            nl.append(text)
        print("\n".join(nl))
        self.configure(text="\n".join(nl))
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

    def create_round_consecutive_line(self, points: list[tuple[int, int]], width: int = 1, color: str = "gray", old_oval_id1 = None, old_line_id = None, old_oval_id2 = None, **kwargs):
        if old_line_id:
            self.delete(old_line_id)
        if old_oval_id1:
            self.delete(old_oval_id1)
        if old_oval_id2:
            self.delete(old_oval_id2)
        for i in range(1, len(points)):
            old_oval_id1 = self.create_oval(points[i-1][0]-width/2, points[i-1][1]-width/2, points[i-1][0]+width/2-1, points[i-1][1]+width/2-1, fill=color, outline=color, **kwargs)
            old_line_id = self.create_line(points[i-1][0], points[i-1][1], points[i][0], points[i][1], fill=color, width=width, **kwargs)
            old_oval_id2 = self.create_oval(points[i][0]-width/2, points[i][1]-width/2, points[i][0]+width/2-1, points[i][1]+width/2-1, fill=color, outline=color, **kwargs)
        return old_oval_id1, old_line_id, old_oval_id2
    def ping_animation(self, points: list[tuple[int, int]], width: int = 1, length = 20, color: str = "green", i = 1, step_dim = 1):
        x1 = points[i-1][0]
        y1 = points[i-1][1]
        h = points[i][1]-points[i-1][1]
        w = points[i][0]-points[i-1][0]
        if w != 0:
            tan = h/w
            dy = step_dim* math.sin(math.atan(tan))
            dx = step_dim* math.cos(math.atan(tan))
        elif h != 0:
            dx = 0
            dy = step_dim* h/abs(h)
        else:
            dx = 0
            dy = 0
        dist = math.sqrt(pow(w,2)+pow(h,2))
        x2 = x1 #+ dx*length
        y2 = y1 #+ dy*length
        trav = 0
        ov1, lin, ov2 = self.create_round_consecutive_line([(x1, y1), (x2, y2)], width, color)
        self.after(1, self.anim_ping, trav, dist, step_dim, dx, dy, (ov1, lin, ov2), x1, y1, x2, y2, i, False, points, width, length, color)
    def anim_ping(self, trav, dist, speed, dx, dy, ids, lx1, ly1, lx2, ly2, i, emblock: bool, *others):
        if trav < others[2]:
            lx2 += dx
            ly2 += dy
            self.coords(ids[1], lx1, ly1, lx2, ly2)
            self.move(ids[2], dx, dy)
            trav += speed
            self.after(5, self.anim_ping, trav, dist, speed, dx, dy, ids,lx1, ly1, lx2, ly2, i,emblock, *others)
        elif trav < dist:
            lx1 += dx
            ly1 += dy
            lx2 += dx
            ly2 += dy
            for eid in ids:
                self.move(eid, dx, dy)
            trav += speed
            self.after(5, self.anim_ping, trav, dist, speed, dx, dy, ids, lx1, ly1, lx2, ly2,i,emblock, *others)
        elif trav < dist + others[2]:
            if i < len(others[0])-1 and not emblock:
                i +=1
                self.ping_animation(*others, i=i)
                emblock = True
            if i == len(others[0])-1 and not emblock:
                i =1
                self.ping_animation(*others, i=i)
                emblock = True
            lx1 += dx
            ly1 += dy
            self.coords(ids[1], lx1, ly1, lx2, ly2)
            self.move(ids[0], dx, dy)
            trav += speed
            self.after(5, self.anim_ping, trav, dist, speed, dx, dy, ids,lx1, ly1, lx2, ly2, i,emblock, *others)
        else:
            for eid in ids:
                self.delete(eid)
            """if i == len(others[0])-1:
                i = 1
                self.ping_animation(*others, i=i)"""



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
    duration: str = None
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

        iconpath = ImageTk.PhotoImage(file=ico_loc)
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
you can use the ENTER button to start fast download

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
        cnv.ping_animation([
            (round((pop_x-opt_height/2-icon_width/2)*dim[0]), round((opt_y-entry_height/2)*dim[1])),
            (round((pop_x-opt_height/2-icon_width/2)*dim[0]), round((opt_y+entry_height/2+opt_height/2)*dim[1])),
            (round(icon_x*dim[0]), round((opt_y+entry_height/2+opt_height/2)*dim[1])),
            (round(icon_x*dim[0]), round((entry_y+entry_height)*dim[1])),
            (round((cut_x-cut_width/2-icon_width/2)*dim[0]), round((entry_y+entry_height)*dim[1])),
            (round((cut_x-cut_width/2-icon_width/2)*dim[0]), round((progbar_y-entry_height/2)*dim[1]))
        ], width=line_dim, length=50)

        self.ctrlz_id = None
        self.ctrlz_txt = [""]
        self.is_closing = False

        self.popup_button = Button(self, "?", pop_x, opt_y, width=pop_dim, height=pop_dim, relative_position=True, relative_dimension=False, state="disabled", color="#777777")
        self.popup_button.rel_place() if self.popup_button.rel_pos else self.popup_button.abs_place()
        PopupManager(self, general_popup_text, [self.popup_button], time=100)



        self.progress_bar = ProgressBar(self, 0.5, progbar_y, width=0.9, relative_position=True, relative_dimension=True)
        self.progress_bar.rel_place()
        self.label = Label(self, "Choose an option", 0.5, 0.8, relative_position=True)
        self.label.rel_place() if self.label.rel_pos else self.label.abs_place()


        # download gui
        self.link_entry = Entry(self, entry_x, entry_y, width=entry_width, height=entry_height, relative_position=True, relative_dimension=True, bg_text="Enter video link...")
        self.link_entry.bind("<KeyRelease>", lambda event: self.infos(event, "Link", self.link_entry))
        self.link_entry.bind("<Control-KeyPress-z>", lambda event: self.ctrlz(event, self.link_entry))
        self.link_entry.bind("<Return>", self.enter_link)

        self.yt_info: list[str] = []
        self.res = None
        self.download_button = Button(self, "Download", button_x, entry_y-entry_height/4, width=button_width+2/dim[0], height=entry_height/2, relative_dimension=True, relative_position=True, command=self.download, border_color=self.cget("fg_color"), border_width=1)
        self.resolution_menu = OptionMenu(self, [], button_x, entry_y+entry_height/4, width=button_width, height=entry_height/2, relative_position=True, relative_dimension=True, title="Resolution", command=self.choose_res)

        # file gui
        self.file_entry = Entry(self, entry_x, entry_y, width=entry_width, height=entry_height, relative_position=True, relative_dimension=True, bg_text="Enter local video file...")
        self.file_entry.bind("<KeyRelease>", lambda event: self.infos(event, "File", self.file_entry))
        self.file_entry.bind("<Control-KeyPress-z>", lambda event: self.ctrlz(event, self.file_entry))
        self.file_entry.bind("<Return>", self.select_file)

        self.check_id = None
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
        if orig_button is not None:
            if any(let.lower() in string.ascii_lowercase for let in start_link.get()) or any(let.lower() in string.ascii_lowercase for let in end_link.get()):
                self.label.set_text("Enter a valid range")
                return
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
        if self.res is None and self.resolution_menu.get() != "Fixed":
            self.label.set_text("Error: choose a resolution")
            self.label.rel_place() if self.label.rel_pos else self.label.rel_place()
            return
        elif self.resolution_menu.get() == "Fixed":
            self.res = "Fixed"
        extracted = self.link_entry.get()
        # print(f"{self.text}: self.extracted set to {self.extracted}")
        path = os.path.join(dwl_dir, self.yt_info[0])
        self.thr = DownloadThread(extracted, path, self.res, self.yt_info[1], self, self.progress_bar, self.label)
        self.thr.start()

        self.res = None


    def select_file(self, event = None):
        dbg.printfunc()
        self.file_loc = fd.askopenfilename()
        if self.file_loc != "":
            self.file_entry.delete(0, ctk.END)
            self.file_entry.insert(0, self.file_loc)
            self.check_id = self.after(5, self.infoThUpd, "File")
            self.label.set_text("Selected file")
        else:
            self.icon_text.configure(text_color="red")
            self.icon_text.set_text("X")
            self.label.set_text("No file was chosen")

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

    def blockz(self, wdg):
        print(f"added {wdg.get()}")
        self.ctrlz_txt.append(wdg.get())
        if len(self.ctrlz_txt) > 30:
            self.ctrlz_txt.pop(0)
    def ctrlz(self, event, wdg):
        print("entered ctrlz")
        print(self.ctrlz_txt)
        wdg.delete(0, ctk.END)
        try:
            self.ctrlz_txt.pop()
            wdg.insert(0, self.ctrlz_txt[-1])
        except IndexError:
            pass
        return "break"

    def infos(self, event, info_type:str, wdg):
        if (event.state & 0x0004 or event.state & 0x20000) and event.keysym != "v":
            return
        if hasattr(self, "it") and self.it.is_alive():
            self.it.stop()
        if self.ctrlz_id:
            self.after_cancel(self.ctrlz_id)
            self.ctrlz_id = None
        if self.check_id is not None:
            self.after_cancel(self.check_id)
        if wdg.get() != "":
            if info_type == "Link":
                chtm = 500
            else:
                chtm = 50
            self.check_id = self.after(chtm, self.infoThUpd, info_type)
        else:
            self.icon_text.set_text("---")
            self.icon_text.configure(text_color="gray")
            if hasattr(self, "it") and self.it.is_alive():
                self.it.stop()
        self.ctrlz_id = self.after(500, self.blockz, wdg)



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
        if ((hasattr(self, "it") and self.it.is_alive()) or (hasattr(self, "thr") and self.thr.is_alive())) and not self.is_closing:
            self.is_closing = True
            # ask widgets
            self.askframe = Frame(self, .5*self.dim[0]-(.8*self.dim[0]/2), 1*self.dim[1], .8, .45, relative_dimension=True, fg_color="#616161")

            self.askframe.rel_place() if self.askframe.rel_pos else self.askframe.abs_place()
            self.anim_move(self.askframe, (.5*self.dim[0]-(.8*self.dim[0]/2), .4*self.dim[1]-(.45*self.dim[1]/2)))
            asklabel = Label(self.askframe, "You have processes in progress.\nAre you sure you want to close the app?", .5,
                             .25, relative_position=True, force_text=False, color="#000000")
            # FIXME: la scritta viene splittata nonostante il \n. penso che sia nel get_maximum_font
            yes = Button(self.askframe, "YES", .25, .6, width=.4, height=.2, relative_position=True, relative_dimension=True,
                         color="#00aa00", command=lambda: self.choose(True), hover_color="#00d100")
            no = Button(self.askframe, "NO", .75, .6, width=.4, height=.2, relative_dimension=True, relative_position=True,
                        color="#aa0000", command=lambda: self.choose(False), hover_color="#d10000")
            set_font(self.askframe, self.font)
            asklabel.rel_place() if asklabel.rel_pos else asklabel.abs_place()
            yes.rel_place() if yes.rel_pos else yes.abs_place()
            no.rel_place() if no.rel_pos else no.abs_place()
        elif self.is_closing:
            self.choose(True)
        else:
            self.destroy()
    def anim_move(self, obj, target: tuple[float, float], speed = 1):
        h = target[1] - obj.y
        w = target[0] - obj.x
        if w != 0:
            tan = h / w
            dy = speed * math.sin(math.atan(tan))
            dx = speed * math.cos(math.atan(tan))
        elif h != 0:
            dx = 0
            dy = speed * h / abs(h)
        else:
            dx = 0
            dy = 0
        trav = 0
        dist = math.sqrt(pow(w,2)+pow(h,2))
        self._anim(obj, trav, dist, speed, dx, dy)
    def _anim(self, obj, trav, dist, speed, dx, dy):
        if trav < dist:
            obj.x += dx
            obj.y += dy
            trav += speed
            obj.kplace()
            self.after(1, self._anim, obj, trav, dist, speed, dx, dy)


    def choose(self, choice: bool):
        if choice:

            if hasattr(self, "it") and self.it.is_alive():
                self.it.stop()
            if hasattr(self, "thr") and self.thr.is_alive():
                self.thr.stop()
            # CHECK: close threads
            # TODO: aggiungi la rimozione ti trm (VideoTrimmer)
            # self.after(2000, self.destroy)
            self.destroy()
        else:
            self.askframe.destroy()
        self.is_closing = False

    def enter_link(self, event):
        if (event.state & 0x0004 or event.state & 0x20000):
            return

        # DOING: fai partire il download subito in qualità "fast"
        # TODO: fai partire subito il thread info
        return "break"

            



if __name__ == "__main__":
    assert os.path.exists(ico_loc)
    dbg.printdb("Started program")
    app = App()
    dbg.printdb("App done")
    app.mainloop()

# TODO: setup wizard
#  aggiungere:
#   Invio con file e link download (ma anche le cut entry). per il download del link, forzi subito l'avvio del
#    infothread, ma se il link non è valido lo segnali nel label generico.
#   aggiungi i requirements.text sia al python App, sia al python CLI
#   in una nuova versione, magari, aggiungi il modo di scaricare un video direttamente in clip
#   quelli in Threads.py
#   aggiungi l'autenticazione, se richiesta
#   aggiungi la possibilità di mandare il "cut" mentre il video si scarica, ma viene avviata solo dopo
#   riprova il download se succede un errore
#  ottimizza:
#   aggiungi dove si può le variabili fisse (dichiarate)

# TODO: V2
#  aggiungi al thread di download la possibilità di cercare il video e di selezionarlo in un menù a tendina
#  aggiungi la preview del video per aiutare a tagliarlo

# TODO: useless
#  label dell'upgrade (e tasto update??)


