import re, string, inspect
def get_text(phrase: str, to_search: tuple[str | None, str | None]):
    try:
        stidx = phrase.index(to_search[0])+ len(to_search[0]) if to_search[0] else 0
    except ValueError:
        stidx = 0
    try:
        enidx = phrase.index(to_search[1]) if to_search[1] else len(phrase)
    except ValueError:
        enidx = len(phrase)
    return phrase[stidx : enidx].strip(" ")


class Time:
    def __init__(self, time: str, format: str):
        """
        Gets info according to format parameter
        :param time: Time to format
        :param format: letters: h, m, s, f (0.f secs). use uppercase to automatically count cyphers between symbols
        :return: Returns
        """
        if any(f not in "hmsfHMSF"+string.punctuation.replace("(", "").replace(")", "") for f in format):
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
        self.minutes += self.seconds//60
        self.seconds %= 60
        self.hour += self.minutes//60
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
                time_idxs[format[idx+1]][1] = True
        raise NotImplementedError("BRUH")
        # TODO: prendi gli indici e mettici gli indici dei valori
    def classic(self) -> str:
        return f"{f'{self.hour:02}:' if self.hour != 0 else ''}{f'{self.minutes:02}:' if self.minutes != 0 else ('00:' if self.hour != 0 else '')}{f'{self.seconds:02}' if self.seconds != 0 else '00'}.{round(self.fsecs/pow(10, len(str(self.fsecs))-3)) if self.fsecs != 0 else '0'}"
    def in_secs(self) -> float:
        return self.hour*3600+self.minutes*60+self.seconds+self.fsecs/pow(10, len(str(self.fsecs)))


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






if __name__ == "__main__":
    tm = Time("00:07:06.13", "H:mm:ss.F")
    print(tm.classic())
    etaT = Time("614.134", "S.F")
    print(etaT.classic())