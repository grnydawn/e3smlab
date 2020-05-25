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

xmlfiles = ("env_archive", "env_batch", "env_build", "env_case",
            "env_mach_pes", "env_mach_specific", "env_run", "env_workflow",
            )

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


class XMLInputs(Base):
    __tablename__ = 'xml_inputs'

    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = Column(VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class PACEDBTBL(App):

    _name_ = "pacedbtbl"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("expid", type=str, nargs="*",
                            help="list of experiment id")
        self.add_argument("-n", "--namelist", metavar="name", type=str,
                            nargs="*", help="list of namelist types")
        self.add_argument("-x", "--xml", metavar="name", type=str,
                            nargs="*", help="list of xml types")
        self.add_argument("-f", "--format", metavar="format", default="tabulator",
                            help="output data format(default: tabulator)")
        self.add_argument("--db-cfg", metavar="path", type=str,
                            help="database configuration data file")
        self.add_argument("--db-session", metavar="session", type=typing.Any,
                            help="database session")
        self.add_argument("--show-namelist", action="store_true",
                            help="show a list of available namelist names")
        self.add_argument("--show-xml", action="store_true",
                            help="show a list of available xml names")
        self.add_argument("-o", "--outfile", metavar="path", type=str,
                            help="outfile path")
        self.add_argument("-p", "--print", action="store_true",
                            help="show output on screen")

        self.register_forward("data", help="formatted namelists")

    def extract_xmlattrs(self, value):

        id = None
        attrs = []

        for key in list(value.keys()):
            if key.startswith("@"):
                if key == "@id":
                    id = value[key]

                else:
                    attrs.append("%s=%s" % (key[1:], self.tostr(value[key])))

                del value[key]

        return id, ", ".join(attrs)

    def gen_xml_tabulator(self, xml, out):

        if isinstance(xml, dict):
            for key, value in xml.items():

                if isinstance(value, dict):
                    name, attrs = self.extract_xmlattrs(value)
                    if name:
                        out.append("{name: '%s', value: '%s', _children:[" % (name, attrs))
                    else:
                        out.append("{name: '%s', value: '%s', _children:[" % (key, attrs))
                    self.gen_xml_tabulator(value, out)
                    out.append("]},")

                elif isinstance(value, list):
                    out.append("{name: '%s', value: '', _children:[" % key)
                    self.gen_xml_tabulator(value, out)
                    out.append("]},")

                else:
                    out.append("{name: '%s', value: '%s'}," % (
                        key, self.tostr(value)))

        elif isinstance(xml, list):

            for idx, value in enumerate(xml):

                if isinstance(value, dict):
                    name, attrs = self.extract_xmlattrs(value)
                    if name:
                        out.append("{name: '%s', value: '%s', _children:[" % (name, attrs))
                    else:
                        out.append("{name: '%d', value: '%s', _children:[" % (idx, attrs))
                    self.gen_xml_tabulator(value, out)
                    out.append("]},")

                elif isinstance(value, list):
                    out.append("{name: '%d', value: '', _children:[" % idx)
                    self.gen_xml_tabulator(value, out)
                    out.append("]},")

                else:
                    out.append("{name: '%d', value: '%s'}," % (
                        idx, self.tostr(value)))

        else:
            print("ELSE")
            import pdb; pdb.set_trace()

    def gen_nml_tabulator(self, nml, out):

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
            text = "'%s'" % value.replace("\n"," ")

        elif isinstance(value, bool):
            if value:
                text = ".true."

            else:
                text = ".false."

        elif value is None:
                text = "none"
        else:
            try:
                x = float(value)
                text = str(value)

            except Exception as err:
                import pdb; pdb.set_trace()
                print(err)

        if escape:
            text = text.replace("'", "\\'")

        return text

    def table_e3smexp(self, expid, nmlname, xmlname):

        nml = self.session.query(NamelistInputs).filter_by(
                    expid=expid, name=nmlname).first()

        if nml and nml.data:
            data = json.loads(nml.data)

            out = []
            getattr(self, "gen_nml_"+self.format, self.gen_nml_tabulator)(data, out)

            if expid in self.fdata:
                names = self.fdata[expid]

            else:
                names = {}
                self.fdata[expid] = names

            names[nmlname] = out

        else:
            print("warining: no namelist found at (%s, %s)." % (expid, nmlname),
                    file=sys.stderr)

        xml = self.session.query(XMLInputs).filter_by(
                    expid=expid, name=xmlname).first()

        if xml and xml.data:
            data = json.loads(xml.data)

            out = []

            getattr(self, "gen_xml_"+self.format, self.gen_xml_tabulator)(data, out)

            if expid in self.fdata:
                names = self.fdata[expid]

            else:
                names = {}
                self.fdata[expid] = names

            names[xmlname] = out

        else:
            print("warining: no namelist found at (%s, %s)." % (expid, xmlname),
                    file=sys.stderr)

    def perform(self, args):

        if args.show_namelist or args.show_xml:
            if args.show_namelist:
                print("\n".join(namelists))

            if args.show_xml:
                print("\n".join(xmlfiles))

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

        if args.xml:
            xlists = [a["_"] for a in args.xml]

        else:
            xlists = xmlfiles


        for expid, namelist, xml in itertools.product(expids, nlists, xlists):
            self.table_e3smexp(expid, namelist, xml)


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
