pacedb
=============

E3SM data loader to PACE database

The tool reads E3SM experiment data and loads it to PACE database. If corresponding table does not exists, it creates tables in database. As of this version of the tool, it uploads various namelists, various xml configurations, makefiles, and rc files.

installation
--------------------

pacedb is installed automatically when **e3smlab** is installed.

Using pacedb as a command-line utility
------------------------------------------
The example shown below reads e3sm experiment file(s) specified in the first argument and upload them to PACE database specified as the second argument. The second db config. argument is a ascii file that has four lines with (username, password, hostname, databasename) per each line::

    >>> e3smlab pacedb <e3sm experiment file or directory> --db-cfg <pace database config. file>

command line arguments::

    Only arguments that are specific to this tool are explained below.

    usage: e3smlab-pacedb [-h] [--forward expr] [--share expr] [--downcast expr]
                          [--import IMPORT] [--assert-in expr] [--assert-out expr]
                          [--assert-forward expr] [--assert-share expr]
                          [--assert-downcast expr] [--version] [--db-cfg DB_CFG]
                          [--db-echo] [--progress] [--verify] [--commit]
                          [--create-expid-table] [--db-session DB_SESSION]
                          datapath

    positional arguments:
      datapath              input data path

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --db-cfg DB_CFG       database configuration data file
      --db-echo             echo database transactions
      --progress            show progress info
      --verify              verify database correctlness
      --create-expid-table  create expid table for development
      --commit              commit database updates
      --db-session DB_SESSION
                            database session

datapath::

    Path to a zipped e3sm datafile or directory of zipped e3sm data files.
    As of this writing, the filename is similar to "exp-ndk-17906.zip".

--db-cfg::

    Path to an ascii file that contains database connection information.
    Only one item should exist in a line.

    mydbcfg.txt:
        username
        password
        hostname
        databasename
    
    example >>> e3smlab pacedb exp-ndk-17906.zip --db-cfg mydbcfg.txt
   
--progress::

    Print the name zipped e3sm data file that is currently being uploaded.
    
    example >>> e3smlab pacedb exp-ndk-17906.zip --db-cfg mydbcfg.txt --progress

--verify::

    Verify database integrity by comparing data between database and zipped e3sm file.

    example >>> e3smlab pacedb exp-ndk-17906.zip --db-cfg mydbcfg.txt --verify
    
--commit::

    Issue commit to update database with this transactions

    example >>> e3smlab pacedb exp-ndk-17906.zip --db-cfg mydbcfg.txt --commit    

--create-expid-table::

    Create a database table that keeps expid only. This is required to use test database.

    example >>> e3smlab pacedb exp-ndk-17906.zip --db-cfg mydbcfg.txt --create-expid-table

--db-session::

    This option is used only in case that this tool is used inside of Python script.
    Please see next section details of usage.

Using pacedb in a Python script
------------------------------------------

**pacedb** can be used inside of Python script. Before using pacedb, please make sure that **e3smlab** is installed properly.

Example::

    from e3smlab import E3SMlab

    # assuming that 'session' is a sqlalchemy session object

    lab = E3SMlab()
    cmd = ["pacedb", "exp-ndk-17906.zip", "--db-session", "@session"]
    ret, _ = lab.run_command(cmd, forward={"session": session})

"E3SMlab" is a driver that runs various e3smlab commands. To see what commands are available, run "e3smlab list".

"cmd" is a list of command-line arguments as explained in previous section.

"--db-session" is an argument to receive sqlalchemy session that is created previously. "@" in "@session" indicates that
actual value will be provided through other than command-line, in this case, by using "forward" argument of "run_command"
function. "forward" is a dictionary to feed namespace to pacedb.

Once successfully completed, selective data in "exp-ndk-17906.zip" will be parsed and uploaded to database through "session".


