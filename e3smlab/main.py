from meteolab import Meteolab
from .nml2json import NML2Json
from .e3smtimestat import E3SMTimeStat
from .inspectcompile import InspectCompile
from .pacedb import PACEDB
from .pacedbnml import PACEDBNML
from .pacedbtbl import PACEDBTBL

class E3SMlab(Meteolab):
    _name_ = "e3smlab"
    _version_ = "0.3.3"
    _description_ = "E3SM Analysis Utilities"
    _long_description_ = "Tools for Analysis of E3SM project"
    _author_ = "Youngsung Kim"
    _author_email_ = "youngsung.kim.act2@gmail.com"
    _url_ = "https://github.com/grnydawn/e3smlab"
    _builtin_apps_ = [NML2Json, E3SMTimeStat, InspectCompile,
                      PACEDB, PACEDBNML, PACEDBTBL]

    def __init__(self):
        pass
        #self.add_argument("--test", help="test argument")
