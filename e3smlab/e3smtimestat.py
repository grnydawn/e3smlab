from microapp import App

import re
import shlex


pat_int = r"[0-9]+"
pat_float = r"[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"
pat_timestat = (r"^(?P<processes>{i})\s(?P<threads>{i})\s(?P<count>{f})\s"
                r"(?P<walltotal>{f})\s(?P<wallmax>{f})\s\(\s*(?P<procmax>{i})\s"
                r"(?P<thrdmax>{i})\s*\)\s(?P<wallmin>{f})\s\(\s*"
                r"(?P<procmin>{i})\s(?P<thrdmin>{i})\s*\)$").format(
                        i=pat_int, f=pat_float)
re_timestat = re.compile(pat_timestat)


class E3SMTimeStat(App):

    _name_ = "e3smtimestat"
    _version_ = "0.1.1"

    def __init__(self, mgr):

        self.add_argument("timestat", type=str, help="e3sm timing stat file")
        self.add_argument("-o", "--outfile", type=str, help="file path")
        self.register_forward("data", help="json object")

    def perform(self, args):

        # data header
        hdr = ("name", "processes", "threads", "count", "walltotal",
                "wallmax", "procmax", "thrdmax", "wallmin", "procmin", "thrdmin")

        rawdata = {}

        for h in hdr:
            rawdata[h]= []

        with open(args.timestat["_"]) as ft:
            for line in ft:
                line = line.strip()

                if not line:
                    continue

                s = shlex.split(line)

                name = s[0]
                rem = " ".join(s[1:])
                match = re_timestat.match(rem)

                if match:
                    rawdata["name"].append(name)
                    rawdata["processes"].append(int(float(match.group("processes"))))
                    rawdata["threads"].append(int(float(match.group("threads"))))
                    rawdata["count"].append(int(float(match.group("count"))))
                    rawdata["walltotal"].append(float(match.group("walltotal")))
                    rawdata["wallmax"].append(float(match.group("wallmax")))
                    rawdata["procmax"].append(int(float(match.group("procmax"))))
                    rawdata["thrdmax"].append(int(float(match.group("thrdmax"))))
                    rawdata["wallmin"].append(float(match.group("wallmin")))
                    rawdata["procmin"].append(int(float(match.group("procmin"))))
                    rawdata["thrdmin"].append(int(float(match.group("thrdmin"))))

                elif rem and rem[0].isdigit() and rem[-1].endswith(")"):
                    # sanity check
                    raise Exception("parsing error : " + line)

        cmd = ["dict2json", "@data"]

        if args.outfile:
            cmd += ["-o", args.outfile["_"]]

        ret, fwds = self.manager.run_command(cmd, forward={"data": rawdata})

        self.add_forward(data=fwds["data"])
