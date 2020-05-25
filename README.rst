e3smlab
=============
Energy Exascale Earth System Model (E3SM) Analysis Tools

**e3smlab** includes a set of software tools and a flexible driver that runs and manages the tools.


installation
--------------------

**e3smlab** supports Python 3.5 or later.

The best way to install **e3smlab** is to use pip Python package installer::

    >>> pip install e3smlab --user --upgrade

All tools explained below in this page are installed automatically when **e3smlab** is installed.

If you prefer to try the latest version of **e3smlab**, you can clone this repository and install it by using setup.py::

    >>> git clone https://github.com/grnydawn/e3smlab
    >>> python3 setup.py install --user

The installation creates a command script of **e3smlab** in a local directory depending on your system. Please make sure that you can run the command as shown below::

    >>> e3smlab

    usage: e3smlab [-h] [--forward expr] [--share expr] [--downcast expr]
                   [--version]
                   [[--] <app> [app-args]] [-- <app> [app-args]]...

    E3SM Analysis Utilities

    optional arguments:
      -h, --help       show this help message and exit
      --forward expr   forward variables to next app
      --share expr     share variables between sibling apps
      --downcast expr  downcast variables under this app
      --version        show program's version number and exit


"**e3smlab** nml2json" command
-------------------------------
The tool converts a gzipped namelist to a json file. The example shown below reads "data.gz" of a gzipped namelist and saves it in "data.json" in JSON format::

    >>> e3smlab nml2json data.gz -o data.json


"**e3smlab** e3smtimestat" command
-------------------------------
The tool converts a E3SM time-stat file to a json file. The example shown below reads "timestat" generated from running a E3SM case and saves it in "timestat.json" in JSON format::

    >>> e3smlab e3smtimestat timestat -o timestat.json

"**e3smlab** inspectcompile" command
-------------------------------
The tool collects compiler command line information generated from running "case.build" in a E3SM case directory, and save it to a json file. The example shown below runs "case.build" script in a given E3SM case path and saves compiler command line information in "e3sm_compile.json" in JSON format::

    >>> e3smlab inspectcompile <e3sm case path> -- dict2json @data -o e3sm_compile.json

"**e3smlab** pacedb" command
-----------------------------------------------------------------------
The tool reads E3SM experiment data and loads it to PACE database. The example shown below reads e3sm experiment file(s) specified in the first argument and upload them to PACE database specified as the second argument. The second db config. argument is a ascii file that has four lines with (username, password, hostname, databasename) per each line::

    >>> e3smlab pacedb <e3sm experiment file or directory> --db-cfg <pace database config. file>

Please see `pacedb<https://github.com/grnydawn/e3smlab/blob/master/README.pacedb.rst>` for details.

"**e3smlab** pacedbnml" command
-----------------------------------------------------------------------
The tool reads e3sm experiment namelists from database and converts them to a format suitable for table viewer. Following example reads e3sm namelists specified by <expid> and <namelist name> from a database specified by "--db-cfg" option. All converted data will be displayed on screen by the "-p" or "--print" option.::

    >>> e3smlab pacedbnml <expid expid ...> --db-cfg <pace db config file> -n <namelist name> -p

Please see `pacedbnml<https://github.com/grnydawn/e3smlab/blob/master/README.pacedbnml.rst>` for details.
