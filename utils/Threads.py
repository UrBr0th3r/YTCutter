from moviepy.editor import VideoFileClip
from proglog import ProgressBarLogger
from time import time, sleep
from datetime import datetime

import sys
import threading
import json
import subprocess
import time
from utils.Utils import *
from tkinter import messagebox
import os

import re

yt_dlp_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "yt-dlp.exe")
ffmpeg_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg.exe")

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
                    self.app.label.set_text(f"Error: {get_text(stderr, ("]", "."))}")
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
                    self.progress_bar.set(1)
                    self.label.set_text(f"Video downloaded in {self.output_loc}")
                    self.app.download_button.configure(state="normal", fg_color=self.app.cut_button.cget("fg_color"))
                os.utime(self.output_loc, (datetime.now().timestamp(), datetime.now().timestamp()))

        except Exception as e:
            print(e)
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
                    self.label.set_text(text=output)
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
                        self.label.set_text(text=f"Downloading {'audio' if mode == 'audio' else 'video'}... {self.perc}%  ETA: {self.eta}")


        #self.proc.wait()
        if not self.stop_bool:
            print(f"\nDone downloading {mode}")
    def merge(self, video_loc:str, audio_loc:str):
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
                    self.label.set_text(text=output)
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
                        self.label.set_text(text=f"Downloading video... {self.perc}%  ETA: {self.eta}")
        if not self.stop_bool:
            print("\nDone fast downloading")


    def stop(self):
        try:
            self.proc.kill()
        except AttributeError:
            pass
        self.stop_bool = True



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
            sleep(1)
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
        self.logger.update_time(time.time())
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
            if start_ins and end_ins:
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
    """info = InfoThread("https://www.youtube.com/watch?v=BOriG-wluJA")
    info.start()
    sleep(2)
    info.stop()"""

    """dwl = DownloadThread("https://www.youtube.com/watch?v=3_X_Hd1XpXE", ".\\boh.mp4", "603", "1141.0")
    dwl.start()
    sleep(10)
    dwl.stop()"""


    print(VideoTrimmer.parse_time("22:1.45"))
    # TODO: cambia Utils.Time con delle regex
    # DOING: prendi info su un file .mp4 esterno, e poi fai anche il download di .mp4 esterno (curl)
    # print(dt.title)





