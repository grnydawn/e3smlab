import sys, os, shutil, json
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from microapp import App

from sqlalchemy import create_engine, ForeignKey, Column
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

rcfiles = ("seq_maps",)

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


class RCInputs(Base):
    __tablename__ = 'rc_inputs'

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
    _version_ = "0.1.4"

    def __init__(self, mgr):

        self.add_argument("datapath", type=str, help="input data path")
        self.add_argument("dbcfg", type=str,  help="database configuration data file")
        self.add_argument("--dbecho", action="store_true",  help="echo database transactions")
        self.add_argument("--progress", action="store_true",  help="show progress info")
        self.add_argument("--verify", action="store_true",  help="verify database correctlness")

        #self.add_argument("-o", "--outfile", type=str, help="file path")
        #self.register_forward("data", help="json object")

    def loaddb_rcfile(self, expid, name, rcpath):
 
        cmd = ["gunzip", rcpath]
        mgr = self.get_manager()
        ret, fwds = mgr.run_command(cmd)

        rcitems = []

        for line in fwds["data"].strip().split("\n"):
            items = tuple(l.strip() for l in line.split(":"))

            if len(items)==2:
                rcitems.append('"%s":%s' % items)

        jsondata = "{%s}" % ",".join(rcitems) 

        if self.verify_db:
            rc = self.session.query(RCInputs).filter_by(
                    expid=expid, name=name).first()

            e3smdump = json.dumps(rc.data, sort_keys=True) if rc else ""
            dbdump = json.dumps(jsondata, sort_keys=True)
            if e3smdump != dbdump:
                print("#######################################################")
                print("rc verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                print(e3smdump)
                print("-------------------------------------------------------")
                print("From database:")
                print(dbdump)
        else:
            rc = RCInputs(expid, name, jsondata)
            self.session.add(rc)

    def loaddb_xmlfile(self, expid, name, xmlpath):
 
        cmd = ["gunzip", xmlpath, "--", "uxml2dict",  "@data", "--",
              "dict2json", "@data"]

        from xml.parsers.expat import ExpatError

        try:
            
            mgr = self.get_manager()
            ret, fwds = mgr.run_command(cmd)

            jsondata = fwds["data"]

            if self.verify_db:
                xml = self.session.query(XMLInputs).filter_by(
                        expid=expid, name=name).first()

                e3smdump = json.dumps(xml.data, sort_keys=True) if xml else ""
                dbdump = json.dumps(jsondata, sort_keys=True)
                if e3smdump != dbdump:
                    print("#######################################################")
                    print("xml verification failure: expid=%d, name=%s" % (expid, name))
                    print("From e3sm experiment:")
                    print(e3smdump)
                    print("-------------------------------------------------------")
                    print("From database:")
                    print(dbdump)
            else:
                xml = XMLInputs(expid, name, jsondata)
                self.session.add(xml)

        except ExpatError as err:
            print("Warning: %s" % str(err))

        except Exception as err:
            print("Warning: %s" % str(err))
            import pdb; pdb.set_trace()
            print(err)

    def loaddb_namelist(self, expid, name, nmlpath):

        cmd = ["gunzip", nmlpath, "--", "nmlread",  "@data", "--",
                 "dict2json", "@data"]

        jsondata = None

        try: 
            mgr = self.get_manager()
            ret, fwds = mgr.run_command(cmd)

            output = list(v for v in fwds)
            jsondata = output[0]["data"]

        except IndexError as err:
            if name.startswith("user_nl"):
                jsondata = ""

            else:
                import pdb; pdb.set_trace()
                raise err
                
        except StopIteration as err:
            print("Warning: %s" % str(err))

        except Exception as err:
            print("Warning: %s" % str(err))
            import pdb; pdb.set_trace()
            print(err)

        if self.verify_db:
            nml = self.session.query(NamelistInputs).filter_by(
                    expid=expid, name=name).first()

            e3smdump = json.dumps(nml.data, sort_keys=True) if nml else ""
            dbdump = json.dumps(jsondata, sort_keys=True)
            if e3smdump != dbdump:
                print("#######################################################")
                print("namelist verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                print(e3smdump)
                print("-------------------------------------------------------")
                print("From database:")
                print(dbdump)

        elif jsondata:
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

                elif prefix in xmlfiles:
                    self.loaddb_xmlfile(expid, prefix, path)

                elif prefix in rcfiles:
                    self.loaddb_rcfile(expid, prefix, path)

                else:
                    pass
                    #print("Warning: %s is not parsed." % basename)
            else:
                pass

    def loaddb_e3smexp(self, zippath):

        head, tail = os.path.split(zippath)
        basename, ext = os.path.splitext(tail)
        items = basename.split("-")

        if ext == ".zip" and len(items)==3:
            expid = int(items[2])

            if not self.verify_db:
                self.session.add(E3SMexp(expid))
                self.session.commit()

            if self.show_progress:
                print("reading %s" % zippath)

            with ZipFile(zippath) as myzip:
                unzipdir = os.path.join(self.tempdir, basename)
                myzip.extractall(path=unzipdir)

                for item in os.listdir(unzipdir):
                    if item.startswith(".") or item in excludes:
                        continue

                    basename, ext = os.path.splitext(item)
                    path = os.path.join(unzipdir, item)

                    if os.path.isdir(path):

                        if basename.startswith("CaseDocs"):
                            self.loaddb_casedocs(expid, path)

                        else:
                            pass
                    else:
                        pass

                if not self.verify_db:
                    self.session.commit()

                shutil.rmtree(unzipdir, ignore_errors=True)

    def perform(self, mgr, args):

        self.show_progress = args.progress
        self.verify_db = args.verify

        inputpath = args.datapath["_"]

        dbcfg = args.dbcfg["_"]
        if not os.path.isfile(dbcfg):
            print("Could not find database configuration file: %s" % cbcfg)
            sys.exit(-1)

        with open(dbcfg) as f:
            myuser, mypwd, myhost, mydb = f.read().strip().split("\n")
            
        dburl = 'mysql+pymysql://%s:%s@%s/%s' % (myuser, mypwd, myhost, mydb)
        engine = create_engine(dburl, echo=args.dbecho)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        with TemporaryDirectory() as self.tempdir:
            if os.path.isdir(inputpath):
                for item in os.listdir(inputpath):
                    self.loaddb_e3smexp(os.path.join(inputpath, item))

            elif os.path.isfile(inputpath):
                self.loaddb_e3smexp(inputpath)

            else:
                print("Can't find input path: %s" % inputpath, file=sys.stderr)
                sys.exit(-1)
