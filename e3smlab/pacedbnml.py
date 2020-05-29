import sys, os, shutil, json, typing, itertools
from microapp import App

from sqlalchemy import create_engine, ForeignKey, Column
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, VARCHAR

namelists = ("atm_in", "atm_modelio", "cpl_modelio", "drv_flds_in", "drv_in",
             "esp_modelio", "glc_modelio", "ice_modelio", "lnd_in",
             "lnd_modelio", "mosart_in", "mpaso_in", "mpassi_in",
             "ocn_modelio", "rof_modelio", "user_nl_cam", "user_nl_clm",
             "user_nl_cpl", "user_nl_mosart", "user_nl_mpascice",
             "user_nl_mpaso", "wav_modelio", "iac_modelio", "docn_in",
             "user_nl_docn", "user_nl_cice", "ice_in")

Base = declarative_base()


class NamelistInputs(Base):
    __tablename__ = 'namelist_inputs'

    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = Column(VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class PACEDBNML(App):

    _name_ = "pacedbnml"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("expid", type=str, nargs="*",
                            help="list of experiment id")
        self.add_argument("-n", "--namelist", metavar="name", type=str,
                            nargs="*", help="list of namelist types")
        self.add_argument("-f", "--format", metavar="format", default="tabulator",
                            help="output data format(default: tabulator)")
        self.add_argument("--db-cfg", metavar="path", type=str,
                            help="database configuration data file")
        self.add_argument("--db-session", metavar="session", type=typing.Any,
                            help="database session")
        self.add_argument("--show-namelist", action="store_true",
                            help="show a list of available namelist names")
        self.add_argument("-o", "--outfile", metavar="path", type=str,
                            help="outfile path")
        self.add_argument("-p", "--print", action="store_true",
                            help="show output on screen")

        self.register_forward("data", help="formatted namelists")

    def gen_tabulator(self, nml, out):

        for gname, group in nml.items():
            if group:
                out.append("{name: '%s', value: '', _children:[" % gname)
                for item, value in group.items():
                    if isinstance(value, dict):
                        out.append("{name: '%s', value: '', _children:[" % item)
                        for k, v in value.items():
                            out.append("{name: '%s', value: '%s'}," % (
                                    k, self.tostr(v)))
                        out.append("]},")
                    else:
                        out.append("{name: '%s', value: '%s'}," % (
                                    item, self.tostr(value)))
                out.append("]},")
            else:
                out.append("{name: '%s', value: ''}," % gname)

    def tostr(self, value, escape=True):

        if isinstance(value, list):
            text = ", ".join([self.tostr(v, False) for v in value])

        elif isinstance(value, str):
            text = "'%s'" % value

        elif isinstance(value, bool):
            if value:
                text = ".true."

            else:
                text = ".false."
        else:
            try:
                x = float(value)
                text = str(value)

            except Exception as err:
                if type(value) == type(u""):
                    text = "'%s'" % value.encode("utf-8")

                else:
                    import pdb; pdb.set_trace()
                    print(err)

        if escape:
            text = text.replace("'", "\\'")

        return text

    def table_e3smexp(self, expid, namelist):

        nml = self.session.query(NamelistInputs).filter_by(
                    expid=expid, name=namelist).first()

        if nml and nml.data:
            data = json.loads(nml.data)

            # for debugging
            #with open("/home/8yk/temp/%s.json" % namelist, "w") as f:
            #    f.write(nml.data)

            out = []
            getattr(self, "gen_"+self.format, self.gen_tabulator)(data, out)

            if expid in self.fdata:
                names = self.fdata[expid]

            else:
                names = {}
                self.fdata[expid] = names

            names[namelist] = out

        else:
            print("warining: no data found at (%s, %s)." % (expid, namelist),
                    file=sys.stderr)


    def perform(self, args):

        if args.show_namelist:
            print("\n".join(namelists))
            sys.exit()

        self.format = args.format["_"]

        if not args.db_session:
            dbcfg = args.db_cfg["_"]
            if not os.path.isfile(dbcfg):
                print("Could not find database configuration file: %s" % cbcfg)
                sys.exit(-1)

            with open(dbcfg) as f:
                myuser, mypwd, myhost, mydb = f.read().strip().split("\n")
                
            dburl = 'mysql+pymysql://%s:%s@%s/%s' % (myuser, mypwd, myhost, mydb)
            engine = create_engine(dburl)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()

        else:
            self.session = args.db_session["_"]

        self.fdata = {}

        expids = [a["_"] for a in args.expid]
        if args.namelist:
            nlists = [a["_"] for a in args.namelist]

        else:
            nlists = namelists

        for expid, namelist in itertools.product(expids, nlists):
            self.table_e3smexp(expid, namelist)


        data = ["["]

        for expid, exp in self.fdata.items():
            if exp: 
                data.append("{name: 'exp-id', value: '%s', _children:[" % expid)

                for name, out in exp.items():
                    if out:
                        data.append("{name: '%s', value: '', _children:[" % name)
                        data.append("".join(out))
                        data.append("]},")

                    else:
                        data.append("{name: '%s', value: ''}," % name)

                data.append("]},")
            else:
                data.append("{name: 'exp-id', value: '%s'}," % expid)

        data.append("]")

        table = "".join(data)

        if args.outfile:
            with open(args.outfile["_"], "w") as f:
                f.write(table)

        if args.print:
            print(table)

        self.add_forward(data=data)
