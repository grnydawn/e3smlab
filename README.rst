e3smlab
=============
Energy Exascale Earth System Model (E3SM) Analysis Tools

**e3smlab** includes a set of software tools and a flexible driver that runs and manages the tools.


installation
--------------------

**e3smlab** supports Python 3.5 and later.

The best way to install **e3smlab** is to use pip3 Python package installer::

    >>> pip3 install e3smlab --user

All tools explained below in this page are installed automatically when **e3smlab** is installed.

If you prefer to try the latest version of **e3smlab**, you can clone this repository and install it by using setup.py::

    >>> git clone https://github.com/grnydawn/e3smlab
    >>> python3 setup.py install --user

The installation creates a command script of **e3smlab** in a local directory depending on your system. Please make sure that you can run the command as shown below::

    >>> e3smlab

    usage: e3smlab [-h] [--forward expr] [--share expr] [--downcast expr]

    optional arguments:
      -h, --help       show this help message and exit
      --forward expr   forward variables to next task
      --share expr     share variables between sibling apps
      --downcast expr  downcast variables under this app


"**e3smlab** nml2json" command
-------------------------------
The tool converts a gzipped namelist to json file. The example shown below reads "data.gz" of a gzipped namelist and saves it in "data.json" in JSON format::

    >>> e3smlab nml2json data.gz -o data.json


"**e3smlab** e3smtimestat" command
-------------------------------
The tool converts a E3SM a time-stat file to json file. The example shown below reads "timestat" generated from running a E3SM case and saves it in "timestat.json" in JSON format::

    >>> e3smlab e3smtimestat timestat -o timestat.json







