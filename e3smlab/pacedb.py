import sys, os, shutil, json, typing
from zipfile import ZipFile
from tempfile import TemporaryDirectory
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

rcfiles = ("seq_maps",)

#makefiles = ("Depends.intel",)
makefiles = ("Depends",)

exclude_zipfiles = []
excludes_casedocs = ["env_mach_specific.xml~"]

Base = declarative_base()


class E3SMexp(Base):
    __tablename__ = 'e3smexp'

    expid = Column(INTEGER(unsigned=True), primary_key=True, index=True)

    def __init__(self, expid):
        self.expid = expid


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


class RCInputs(Base):
    __tablename__ = 'rc_inputs'

    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = Column(VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class MakefileInputs(Base):
    __tablename__ = 'makefile_inputs'

    expid = Column(INTEGER(unsigned=True), ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = Column(VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class PACEDB(App):

    _name_ = "pacedb"
    _version_ = "0.1.8"

    def __init__(self, mgr):

        self.add_argument("datapath", type=str, nargs="+", help="input data path")
        self.add_argument("--db-cfg", type=str,  help="database configuration data file")
        self.add_argument("--db-echo", action="store_true",  help="echo database transactions")
        self.add_argument("--progress", action="store_true",  help="show progress info")
        self.add_argument("--verify", action="store_true",  help="verify database correctlness")
        self.add_argument("--commit", action="store_true",  help="commit database updates")
        self.add_argument("--create-expid-table", action="store_true",  help="create expid table for development")
        self.add_argument("--db-session", type=typing.Any,  help="database session")

        #self.add_argument("-o", "--outfile", type=str, help="file path")
        #self.register_forward("data", help="json object")

    def loaddb_makefile(self, expid, name, makefile):
  
        cmd = ["gunzip", makefile, "--", "parsemk",  "@data"]

        mgr = self.get_manager()
        ret, fwds = mgr.run_command(cmd)

        mkitems = []

        for item in fwds["data"]:
            mkitems.append(item.to_source())

        jsondata = json.dumps(mkitems)

        #try:
        mk = self.session.query(MakefileInputs).filter_by(
                expid=expid, name=name).first()

        if self.verify_db:
            if not mk or jsondata != mk.data:
                print("#######################################################")
                print("makefile verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                print(jsondata)
                print("-------------------------------------------------------")
                print("From database:")
                print(mk.data if mk else mk)
        else:
            if mk:
                print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

            else:
                mk = MakefileInputs(expid, name, jsondata)
                self.session.add(mk)

        #except (InvalidRequestError, IntegrityError) as err:
        #    print("Missing expid in database: expid=%d, makefile-name=%s" % (expid, name))


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

        #try:
        rc = self.session.query(RCInputs).filter_by(
                expid=expid, name=name).first()

        if self.verify_db:
            #e3smdump = json.dumps(rc.data, sort_keys=True) if rc else ""
            #dbdump = json.dumps(jsondata, sort_keys=True)
            #if e3smdump != dbdump:
            if not rc or jsondata != rc.data:
                print("#######################################################")
                print("rc verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                #print(e3smdump)
                print(jsondata)
                print("-------------------------------------------------------")
                print("From database:")
                #print(dbdump)
                print(rc.data if rc else rc)
        else:
            if rc:
                print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

            else:
                rc = RCInputs(expid, name, jsondata)
                self.session.add(rc)

        #except (InvalidRequestError, IntegrityError) as err:
        #    print("Missing expid in database: expid=%d, rc-name=%s" % (expid, name))

    def loaddb_xmlfile(self, expid, name, xmlpath):
 
        cmd = ["gunzip", xmlpath, "--", "uxml2dict",  "@data", "--",
              "dict2json", "@data"]

        from xml.parsers.expat import ExpatError

        mgr = self.get_manager()
        ret, fwds = mgr.run_command(cmd)

        jsondata = fwds["data"]

        try:
            xml = self.session.query(XMLInputs).filter_by(
                    expid=expid, name=name).first()

            if self.verify_db:
                #e3smdump = json.dumps(xml.data, sort_keys=True) if xml else ""
                #dbdump = json.dumps(jsondata, sort_keys=True)
                #if e3smdump != dbdump:
                if not xml or jsondata != xml.data:
                    print("#######################################################")
                    print("xml verification failure: expid=%d, name=%s" % (expid, name))
                    print("From e3sm experiment:")
                    #print(e3smdump)
                    print(jsondata)
                    print("-------------------------------------------------------")
                    print("From database:")
                    #print(dbdump)
                    print(xml.data if xml else xml)
            else:
                if xml:
                    print("Insertion is discarded due to dupulication: expid=%d, xml-name=%s" % (expid, name))

                else:
                    xml = XMLInputs(expid, name, jsondata)
                    self.session.add(xml)

        except ExpatError as err:
            print("Warning: %s" % str(err))

        #except (InvalidRequestError, IntegrityError) as err:
        #    print("Missing expid in database: expid=%d, xml-name=%s" % (expid, name))

        #except Exception as err:
        #    print("Warning: %s" % str(err))
        #    import pdb; pdb.set_trace()
        #    print(err)

    def loaddb_namelist(self, expid, name, nmlpath):

        cmd = ["gunzip", nmlpath, "--", "nmlread",  "@data", "--",
                 "dict2json", "@data"]

        jsondata = None

        try:
            mgr = self.get_manager()
            ret, fwds = mgr.run_command(cmd)

            jsondata = fwds["data"]

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

        #try:
        nml = self.session.query(NamelistInputs).filter_by(
                    expid=expid, name=name).first()

        if self.verify_db:
            #e3smdump = json.dumps(nml.data, sort_keys=True) if nml else ""
            #dbdump = json.dumps(jsondata, sort_keys=True)
            #if e3smdump != dbdump:
            if not nml or jsondata != nml.data:
                print("#######################################################")
                print("namelist verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                #print(e3smdump)
                print(jsondata)
                print("-------------------------------------------------------")
                print("From database:")
                #print(dbdump)
                print(nml.data if nml else nml)

        elif jsondata:
            if nml:
                print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

            else:
                nml = NamelistInputs(expid, name, jsondata)
                self.session.add(nml)

        #except (InvalidRequestError, IntegrityError) as err:
        #    print("Missing expid in database: expid=%d, namelist-name=%s" % (expid, name))

    def loaddb_casedocs(self, expid, casedocpath):

        for item in os.listdir(casedocpath):
            basename, ext = os.path.splitext(item)
            path = os.path.join(casedocpath, item)
            if any(basename.startswith(e) for e in excludes_casedocs):
                continue

            if os.path.isfile(path) and ext == ".gz":
                #prefix, _ = basename.split(".", 1)
                nameseq = []
                for n in basename.split("."):
                    if n.isdigit():
                        break
                    nameseq.append(n)
                name = ".".join(nameseq)

                if nameseq[0] in namelists:
                    self.loaddb_namelist(expid, name, path)

                elif nameseq[0] in xmlfiles:
                    self.loaddb_xmlfile(expid, name, path)

                elif nameseq[0] in rcfiles:
                    self.loaddb_rcfile(expid, name, path)

                elif nameseq[0] in makefiles:
                    self.loaddb_makefile(expid, name, path)

#                elif any(basename.startswith(p) for p in makefiles):
#                    for makefile in makefiles:
#                        if basename.startswith(makefile):
#                            self.loaddb_makefile(expid, makefile, path)
#                            break
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

            if not self.verify_db and self.create_expid_table:

                    try:
                        self.session.add(E3SMexp(expid))
                        if self.commit_updates:
                            self.session.commit()

                    except (InvalidRequestError, IntegrityError) as err:
                        print("Warning: database integrity error: %s" % str(err))
                        self.session.rollback()
                        return

            if self.show_progress:
                print("reading %s" % zippath)

            with ZipFile(zippath) as myzip:

                unzipdir = os.path.join(self.tempdir, basename)
                myzip.extractall(path=unzipdir)

                try:
                    for item in os.listdir(unzipdir):
                        if item.startswith(".") or item in exclude_zipfiles:
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

                            if self.commit_updates:
                                self.session.commit()

                            else:
                                print("INFO: pacedb ended without committing any "
                                      "staged database transaction.")

                except (InvalidRequestError, IntegrityError) as err:
                    print("Warning: database integrity error at %s: %s" % (zippath, str(err)))
                    self.session.rollback()

                finally:                
                    shutil.rmtree(unzipdir, ignore_errors=True)

    def perform(self, args):

        self.show_progress = args.progress
        self.verify_db = args.verify
        self.create_expid_table = args.create_expid_table
        self.commit_updates = args.commit

        for datapath in args.datapath:
            inputpath = datapath["_"]

            if not args.db_session:
                dbcfg = args.db_cfg["_"]
                if not os.path.isfile(dbcfg):
                    print("Could not find database configuration file: %s" % dbcfg)
                    sys.exit(-1)

                with open(dbcfg) as f:
                    myuser, mypwd, myhost, mydb = f.read().strip().split("\n")
                    
                dburl = 'mysql+pymysql://%s:%s@%s/%s' % (myuser, mypwd, myhost, mydb)
                engine = create_engine(dburl, echo=args.db_echo)
                Base.metadata.create_all(engine)
                Session = sessionmaker(bind=engine)
                self.session = Session()

            else:
                self.session = args.db_session["_"]

            with TemporaryDirectory() as self.tempdir:
                if os.path.isdir(inputpath):
                    for item in os.listdir(inputpath):
                        self.loaddb_e3smexp(os.path.join(inputpath, item))

                elif os.path.isfile(inputpath):
                    self.loaddb_e3smexp(inputpath)

                else:
                    print("Can't find input path: %s" % inputpath, file=sys.stderr)
                    sys.exit(-1)
