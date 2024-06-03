import os
import argparse
import string
import sys
import yt_dlp
import ctypes
from moviepy.video.io.VideoFileClip import VideoFileClip as vfc



env_loc = os.getenv("USERPROFILE")
download_dir = os.path.join(env_loc, "Downloads\\")

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


"""
ytdlp_dir = env_loc+"\\ytcutter\\ytdlp\\"
ytdlp_loc = "yt-dlp.exe"
ffmpeg_dir = env_loc+"\\ytcutter\\ffmpeg\\"
ffmpeg_loc = "ffmpeg.exe"
ffmpeg_link = "https://github.com/GyanD/codexffmpeg/releases/download/2024-05-27-git-01c7f68f7a/ffmpeg-2024-05-27-git-01c7f68f7a-full_build.zip"
ytdlp_link = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
"""
"""
def install(loc: str, file: str, link: str, *, is_zip: bool = False) -> bool:
    if not os.path.exists(loc):
        os.makedirs(loc)
    if not os.path.exists(loc+file):
        print("Missing {}. Installing...".format(file))
        data = requests.get(link).content
        if not is_zip:
            with open(loc+file, "wb") as exe:
                exe.write(data)
                exe.close()
        else:
            file_type = link[link.rindex("."):]
            zip_loc = loc+file[:file.index(".")]+file_type
            with open(zip_loc, "wb") as zipped:
                zipped.write(data)
                zipped.close()
            zip_dir = zip_loc[:zip_loc.rindex(".")]
            os.makedirs(zip_dir)
            with zipfile.ZipFile(zip_loc, "r") as archive:
                archive.extractall(zip_dir)
                archive.close()
            os.remove(zip_loc)
            link_path: str|None = None
            for path, dirs, files in os.walk(zip_dir):
                if file in files:
                    link_path = os.path.join(path, file)
            if link_path is None:
                return False
            os.link(link_path, loc+file)
        print(f"{file} successfully installed in {loc+file}")
    return True
"""


class InputArgs:
    link: str = ""
    range: str = None
    start: str = None
    end: str = None
    output: str = None
    file: str = ""

    def __init__(self):
        choose = 0
        while choose != 1 and choose != 2:
            try:
                choose = int(
                    input("1) Download and crop a video from its youtube URL\n2) Crop a video file\nChoose (1/2): "))
                if choose != 1 and choose != 2:
                    raise ValueError
            except ValueError:
                choose = 0
                print("Invalid input")
        if choose == 1:
            while self.link == "":
                self.link = input("Enter YouTube video URL: ")
        else:
            while self.file == "":
                self.file = input("Enter video file path: ")
        print("Enter the time frame to crop. Press enter to download the full video. You can crop multiple time frames.\n"
            "If you want to crop only the start or the end, just leave blank the part you want to keep.\n"
            "Examples:\n"
            "(Both-end range) 43.54.2:32.54 -> Outputs the clip from 43.54.200 to 32.54.000\n"
            "(Cut until ... ) 4.52:end -> Outputs the clip from 4.52.000 to the end\n"
            "(Keep from start to ... ) :3.24 -> Outputs the clip from start to 3.24.000\n"
            "(Cut more ranges) 4.32:5.7.1 ; 2.10:6.01.2 -> Outputs two clips. Their timeframe refers to both-end range\n")
        time = ""
        while time == "":
            try:
                time = input("Enter the range: ")
                if any(":" not in x for x in time.split(";")) or any(x.count(":") > 1 for x in time.split(";")):
                    raise ValueError("Invalid input")
            except ValueError as e:
                time = ""
                print(e)



        if ";" in time or (";" not in time and not any(types in time.split(":") for types in ["", "start", "end"])):
            self.range = time
        elif "start" in time or "" == time.split(":")[0].strip():
            self.end = time.split(":")[1]
        elif "end" in time or "" == time.split(":")[1].strip():
            self.start = time.split(":")[0]





if __name__ == "__main__":
    filename = sys.argv[0]



    # args
    parser = argparse.ArgumentParser(description="Downloads files from youtube link")
    parser.add_argument("-l", "--link", type=str, help="Youtube video link")
    parser.add_argument("-r", "--range", type=str, help="Specify range of time to download: [sMin.sSec(.sMs):eMin.eSec(.eMs)]. It is possible to insert multiple clips: [(sMin.sSec:eMin.eSec);(sMin.sSec:eMin.eSec)]. You can leave blank one side to tell that the clip has to go from/to the start/end")
    parser.add_argument("-s", "--start", type=str, help="Specify start time to download. [min.sec(.ms)]")
    parser.add_argument("-e", "--end", type=str, help="Specify end time to download. [min.sec(.ms)]")
    parser.add_argument("-o", "--output", type=str, help="Specify output name.")
    parser.add_argument("-f", "--file", type=str, help="Crop a video specified with this flag")
    args = parser.parse_args()

    if not args.link and not args.file:

        args = InputArgs()

    """
    #install exes if not in dirs
    if not install(ytdlp_dir, ytdlp_loc, ytdlp_link):
        print("Could not install {}".format(ytdlp_loc))
    if not install(ffmpeg_dir, ffmpeg_loc, ffmpeg_link, is_zip=True):
        print("Could not install {}".format(ffmpeg_loc))
    """

    # arg parser checks
    try:

        result = []
        if args.range:
            pairs = args.range.split(";")
            for pair in pairs:
                split = pair.split(':')
                if len(split) != 2:
                    raise ValueError("A range has too many values")
                for f in split:
                    result.append(f)
        #print(result)

        if (args.link and args.file):
            raise ValueError("Invalid input. You have to define a link or a file (not both). Check {} -h".format(filename))
        if args.link and "youtube.com" not in args.link and "youtu.be" not in args.link:
            raise ValueError("Invalid Youtube URL")
        if (args.start or args.end) and args.range:
            print("Used two conflicting tags. Using range")
        if (args.start or args.end or args.range) and any(x in y for x in ["[", "]"] for y in [args.start if args.start is not None else "", args.end if args.end is not None else "", args.range if args.range is not None else ""]):
            raise ValueError(f"Flag has to be used without square brackets. Example: -s 43.25. Check {filename} -h")
        if (args.start or args.end or args.range) and \
                (any(c in t for c in string.ascii_letters+string.punctuation.translate(str.maketrans("","", ". ;")) for t in [args.start if args.start is not None else "", args.end if args.end is not None else ""]+(result if args.range is not None else []))):
            #print(args.range, any(c in t for c in string.ascii_letters+string.punctuation.strip(".()") for t in [args.start if args.start is not None else "", args.end if args.end is not None else ""]+(args.range.split(":") if args.range is not None else [])), any("." not in t for t in args.range.split(":")), )
            """for c in string.ascii_letters+string.punctuation.translate(str.maketrans("","", ".();")):
                for t in [args.start if args.start is not None else "", args.end if args.end is not None else ""]+(result if args.range is not None else []):
                    if c in t:
                        print(c, t)"""
            raise ValueError(f"Error to parse time argument, check {filename} -h")
        if args.output and not args.output.endswith(".mp4"):
            args.output += ".mp4"
        if args.output and os.path.exists(download_dir+args.output):
            raise ValueError(f"Error: {args.output} already exists")
    except ValueError as e:
        print(e)
        sys.exit(1)
    if args.link:
        # download video
        print(f"Downloading {args.link}")
        ytdl_opts = {
            'format': 'best'
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            title = ydl.extract_info(args.link, download=False).get("title", None)
        title = title.replace(" ", "_").translate(str.maketrans("","", string.punctuation.replace("_", "")))+".mp4" if not args.output else args.output[:-4]+"_tmp"+args.output[-4:]
        ytdl_opts["outtmpl"] = download_dir+title
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            ydl.download([args.link])
        video_loc = download_dir+title
    else:
        video_loc = args.file
        title = os.path.basename(video_loc)
    # args.range to start:end
    start_args: list[str | None] = []
    end_args: list[str | None] = []
    if args.range:
        times = args.range.split(";")

        start_args = [time.split(":")[0].strip() if time.split(":")[0].strip() != "" else None for time in times]
        end_args = [time.split(":")[1].strip() if time.split(":")[1].strip() != "" else None for time in times]


    if args.start and not args.end:
        start_args = [args.start]
        end_args = [None]

    if not args.start and args.end:
        start_args = [None]
        end_args = [args.end]

    if args.start and not args.end:
        start_args = [args.start]
        end_args = [args.end]



    try:
        if len(start_args) != 0 or len(end_args) != 0:
            assert len(start_args) == len(end_args)
            video_clip = vfc(video_loc)
            for i in range(len(start_args)):
                if not args.output:
                    title = title[:title.rindex(".mp4")] + title[title.rindex(".mp4") + 4:]
                    if len(start_args) > 1:
                        title += f"_{i+1}"
                    if start_args[i] and not end_args[i]:
                        title += f"_[{start_args[i]}-end]"
                    if end_args[i] and not start_args[i]:
                        title += f"_[start-{end_args[i]}]"

                    if start_args[i] and end_args[i]:
                        title += f"_[{start_args[i]}-{end_args[i]}]"
                    title += ".mp4"
                else:
                    title = args.output[:args.output.rindex(".mp4")] + args.output[args.output.rindex(".mp4") + 4:]
                # TODO: check if the number has just one value (just seconds)
                start = float(start_args[i].split(".")[0])*60+float(start_args[i].split(".")[1]) if start_args[i] is not None else None
                if start_args[i] is not None:
                    try:
                        start += float(start_args[i].split(".")[2])/pow(10, len(start_args[i].split(".")[2]))
                    except IndexError:
                        pass
                end = float(end_args[i].split(".")[0])*60+float(end_args[i].split(".")[1]) if end_args[i] is not None else None
                if end_args[i] is not None:
                    try:
                        end += float(end_args[i].split(".")[2])/pow(10, len(end_args[i].split(".")[2]))
                    except IndexError:
                        pass
                print(f"Cutting {video_loc} to {start_args[i] if start_args[i] is not None else "start"}:{end_args[i] if end_args[i] is not None else "end"}")
                if (start < 0 or start > video_clip.duration) or (end < 0 or end > video_clip.duration) or end < start:
                    video_clip.close()
                    raise ValueError(f"Error in time value, check {filename} -h")
                print((start if start is not None else 0, end if end is not None else video_clip.duration))
                cut_clip = video_clip.subclip(start if start is not None else 0, end if end is not None else video_clip.duration)
                cut_clip.write_videofile(download_dir+title)
                cut_clip.close()
            video_clip.close()
            if not args.file:
                os.remove(video_loc)
    except ValueError as e:

        print(e)
        os.rename(video_loc, video_loc[:video_loc.rindex("_tmp")]+video_loc[video_loc.rindex("_tmp")+4:])
        title = video_loc[:video_loc.rindex("_tmp")]+video_loc[video_loc.rindex("_tmp")+4:]
        print("Keeping integral video")
    finally:
        print(f"Video {title} downloaded in {download_dir}")
        input("Press enter to exit the program... ")




