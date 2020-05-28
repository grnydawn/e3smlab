pacedbnml
=============

E3SM namelist converter to a format usable in table viewer

The tool reads E3SM experiment namelist from database and convert it to a format usuable in table viewer. As of this version of the tool, it supports Tabulator format only.

installation
--------------------

pacedbnml is installed automatically when **e3smlab** is installed.

Using pacedbnml as a command-line utility
------------------------------------------
The example shown below reads e3sm experiments specified by a list of positional argument of experiment ids and converts their namelists to a one of table format, Tabulator in this case as a default format. The "--db-cfg" option is a path to a file that is a ascii file that has four lines with (username, password, hostname, databasename) per each line::

    >>> e3smlab pacedbnml <expid expid ...> --db-cfg <pace db config file> -n <namelist name> -p

command line arguments::

    Only arguments that are specific to this tool are explained below.

    usage: e3smlab-pacedbnml [-h] [--forward expr] [--share expr]
                             [--downcast expr] [--import IMPORT]
                             [--assert-in expr] [--assert-out expr]
                             [--assert-forward expr] [--assert-share expr]
                             [--assert-downcast expr] [--version]
                             [-n [name [name ...]]] [-f format] [--db-cfg path]
                             [--db-session session] [--show-namelist] [-o path]
                             [-p]
                             [expid [expid ...]]

    positional arguments:
      expid                 list of experiment id

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -n [name [name ...]], --namelist [name [name ...]]
                            list of namelist types
      -f format, --format format
                            output data format(default: tabulator)
      --db-cfg path         database configuration data file
      --db-session session  database session
      --show-namelist       show a list of available namelist names
      -o path, --outfile path
                            outfile path
      -p, --print           show output on screen

expid::

    an experiment number. In following example, only "2" is specified as an experiment id.

    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt -n atm_in -p

--db-cfg::

    Path to an ascii file that contains database connection information.
    Only one item should exist in a line.

    mydbcfg.txt:
        username
        password
        hostname
        databasename
    
    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt -n atm_in -p
   
--namelist, --show-namelist::

    a list of namelist names that will be converted to table format. In following example
    only atm_in namelist is specified. Please find --show-namelist option to see all
    namelist names available.
    
    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt --namelist atm_in -p

--outfile::

    Create  an ascii file of converted namelist

    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt --namelist atm_in --outfile atm_in.tbl

--print::

    Show output on screen.

    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt --namelist atm_in --print

--format::

    Output format of namelist. As of this version, only Tabulator format is supported.

    example >>> e3smlab pacedbnml 2 --db-cfg mydbcfg.txt --namelist atm_in --print --format tabulator

--db-session::

    This option is used only in case that this tool is used inside of Python script.
    Please see next section details of usage.

Using pacedbnml in a Python script
------------------------------------------

**pacedbnml** can be used inside of Python script. Before using pacedbnml, please make sure that **e3smlab** is installed properly.

Example::

    from e3smlab import E3SMlab

    # assuming that 'session' is a sqlalchemy session object

    lab = E3SMlab()

    cmd = ["pacedbnml", "2", "--db-session", "@session", "--outfile", "nml.tbl"]
    ret, _ = lab.run_command(cmd, forward={"session": session})

"E3SMlab" is a driver that runs various e3smlab commands. To see what commands are available, run "e3smlab list".

"cmd" is a list of command-line arguments as explained in previous section.

"--db-session" is an argument to receive sqlalchemy session that is created previously. "@" in "@session" indicates that
actual value will be provided through other than command-line, in this case, by using "forward" argument of "run_command"
function. "forward" is a Python dictionary to feed namespace to pacedb.

Once successfully completed, all namelists of experiment 2 will be downloaded from database and  will be saved in "nml.tbl" file.
