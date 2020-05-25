from microapp import App


class NML2Json(App):

    _name_ = "nml2json"
    _version_ = "0.1.1"

    def __init__(self, mgr):

        self.add_argument("zipfile", type=str, help="zipped file")
        self.add_argument("-o", "--outfile", type=str, help="file path")
        self.register_forward("data", help="json object")

    def perform(self, args):

        cmd = ["gunzip", args.zipfile["_"], "--", "nmlread",  "@data", "--",
                 "dict2json", "@data"]

        if args.outfile:
            cmd += ["-o", args.outfile["_"]]

        ret, fwds = self.manager.run_command(cmd)

        self.add_forward(data=fwds["data"])
