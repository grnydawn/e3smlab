import sys, os
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from microapp import App, run_command

#from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, VARCHAR
#from sqlalchemy.dialects.mysql import \
#        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
#        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
#        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
#        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
#        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

namelists = ("atm_in", "atm_modelio", "cpl_modelio", "drv_flds_in", "drv_in",
             "esp_modelio", "glc_modelio", "ice_modelio", "lnd_in",
             "lnd_modelio", "mosart_in", "mpaso_in", "mpassi_in",
             "ocn_modelio", "rof_modelio", "user_nl_cam", "user_nl_clm",
             "user_nl_cpl", "user_nl_mosart", "user_nl_mpascice",
             "user_nl_mpaso", "wav_modelio")
excludes = []
Base = declarative_base()


class E3SMexp(Base):
    __tablename__ = 'e3smexp'

    expid = Column(INTEGER(unsigned=True), primary_key=True, index=True)

    def __init__(self, expid):
        self.expid = expid


class NamelistInputs(Base):
    __tablename__ = 'namelist_inputs'

    id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True)
    name = Column(VARCHAR(100), nullable=False, index=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class XMLInputs(Base):
    __tablename__ = 'xml_inputs'

    id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True)
    name = Column(VARCHAR(100), nullable=False, index=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class PACEDB(App):

    _name_ = "pacedb"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("datadir", type=str, help="input data directory")
        self.add_argument("--password", type=str, help="database password")
        #self.add_argument("-o", "--outfile", type=str, help="file path")
        #self.register_forward("data", help="json object")

    def loaddb_namelist(self, expid, name, nmlpath):

        cmd = ["gunzip", nmlpath, "--", "nmlread",  "@data", "--",
                 "dict2json", "@data"]

        try:
            ret, fwds = run_command(self, cmd)

            output = list(v for v in fwds.values())
            jsondata = output[0]["data"]
        except IndexError as err:
            if name.startswith("user_nl"):
                jsondata = ""

            else:
                raise err
                
        except Exception as err:
            print(err)
            import pdb; pdb.set_trace()
            print(err)

        nml = NamelistInputs(expid, name, jsondata)
        self.session.add(nml)

    def loaddb_casedocs(self, expid, casedocpath):

        for item in os.listdir(casedocpath):
            basename, ext = os.path.splitext(item)
            path = os.path.join(casedocpath, item)

            if os.path.isfile(path) and ext == ".gz":
                prefix, _ = basename.split(".", 1)

                if prefix in namelists:
                    self.loaddb_namelist(expid, prefix, path)

                else:
                    pass
            else:
                pass

    def loaddb_e3smexp(self, expid, zippath):

        with ZipFile(zippath) as myzip:
            myzip.extractall(path=self.tempdir)

            for item in os.listdir(self.tempdir):
                basename, ext = os.path.splitext(item)
                path = os.path.join(self.tempdir, item)

                if item.startswith(".") or item in excludes:
                    continue

                if os.path.isdir(path):

                    if basename.startswith("CaseDocs"):
                        self.loaddb_casedocs(expid, path)

                    else:
                        pass
                else:
                    pass

            self.session.commit()

    def perform(self, mgr, args):

        inputdir = args.datadir["_"]
        if not os.path.isdir(inputdir):
            print("Can't find input directory: %s" % inputdir, file=sys.stderr)
            sys.exit(-1)

        # connect to db
        # mysql -u ykim -p
        myuser, mypwd, myhost, mydb = "ykim", "exascale2020performance", "localhost", "ytestbed"
        dburl = 'mysql+pymysql://' + myuser + ':' + mypwd + '@' + myhost +  '/' + mydb
        engine = create_engine(dburl, echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # select the top table of e3sm case

        with TemporaryDirectory() as self.tempdir:
            for item in os.listdir(inputdir):
                basename, ext = os.path.splitext(item)
                path = os.path.join(inputdir, item)

                if os.path.isfile(path) and ext == ".zip":
                    _, _, _expid = basename.split("-")
                    expid = int(_expid)
                    self.session.add(E3SMexp(expid))
                    self.session.commit()
                    self.loaddb_e3smexp(expid, path)

                break # for dev.
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


