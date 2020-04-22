from microapp import App, run_command


class NML2Json(App):

    _name_ = "nml2json"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("zipfile", type=str, help="zipped file")
        self.add_argument("-o", "--outfile", type=str, help="file path")
        self.register_forward("data", help="json object")

    def perform(self, mgr, args):

        cmd = ["gunzip", args.zipfile["_"], "--", "nmlread",  "@data", "--",
                 "dict2json", "@data"]

        if args.outfile:
            cmd += ["-o", args.outfile["_"]]

        ret, fwds = run_command(self, cmd)

        output = list(v for v in fwds.values())
        self.add_forward(data=output[0]["data"])
