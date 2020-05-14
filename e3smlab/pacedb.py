import sys, os
from microapp import App, run_command
from zipfile import ZipFile
import mysql.connector as mariadb


class PACEDB(App):

    _name_ = "pacedb"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("datadir", type=str, help="input data directory")
        self.add_argument("--password", type=str, help="database password")
        #self.add_argument("-o", "--outfile", type=str, help="file path")
        #self.register_forward("data", help="json object")

    def loaddb_folder(self, zipobj, member):
        import pdb; pdb.set_trace()

    def loaddb_e3smcase(self, path):

        with ZipFile(path) as myzip:
            for member in myzip.infolist():
                if member.orig_filename.startswith(".") or member in []:
                    continue

                if member.is_dir():
                    self.loaddb_folder(myzip, member)

                else:
                    import pdb; pdb.set_trace()
            #with myzip.open('eggs.txt') as myfile:
            #    print(myfile.read())

    def perform(self, mgr, args):

        inputdir = args.datadir["_"]
        if not os.path.isdir(inputdir):
            print("Can't find input directory: %s" % inputdir, file=sys.stderr)
            sys.exit(-1)

        # connect to db
        mariadb_connection = mariadb.connect(user='ykim',
                    password=args.password["_"], database='ytestbed')

        cursor = mariadb_connection.cursor()
        import pdb; pdb.set_trace()

        # select the top table of e3sm case


        for item in os.listdir(inputdir):
            basename, ext = os.path.splitext(item)
            path = os.path.join(inputdir, item)

            if os.path.isfile(path) and ext == ".zip":
                self.loaddb_e3smcase(path)
#
#        cmd = ["gunzip", args.zipfile["_"], "--", "nmlread",  "@data", "--",
#                 "dict2json", "@data"]
#
#        if args.outfile:
#            cmd += ["-o", args.outfile["_"]]
#
#        ret, fwds = run_command(self, cmd)
#
#        output = list(v for v in fwds.values())
#        self.add_forward(data=output[0]["data"])


