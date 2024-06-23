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
import re

pattern = re.compile(r'^(?:(\d{1,2}):)?(?:(\d{1,2}):)?(\d{1,2})(\.\d+)?$')

test_strings = ['22:1.45', '1:22:1.45', '1.45', ":1.45", ".45", "1:"]

for test in test_strings:
    match = pattern.match(test)
    if match:
        print(f"Input: {test}")
        print(f"Groups: {match.groups()}")
        for i in range(len(match.groups())):
            print(float(match.group(i+1)) if match.group(i+1) else 0)
    else:
        print(f"Input: {test} did not match")
