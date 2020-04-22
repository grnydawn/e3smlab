from microapp import Project
from .nml2json import NML2Json

class E3SMLab(Project):
    _name_ = "e3smlab"
    _version_ = "0.1.0"
    _description_ = "E3SM Analysis Utilities"
    _long_description_ = "Tools for Analysis of E3SM project"
    _author_ = "Youngsung Kim"
    _author_email_ = "youngsung.kim.act2@gmail.com"
    _url_ = "https://github.com/grnydawn/e3smlab"
    _builtin_apps_ = [NML2Json]

    def __init__(self):
        pass
        #self.add_argument("--test", help="test argument")
