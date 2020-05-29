import sys, os, subprocess

here = os.path.dirname(os.path.abspath(__file__))
home = os.path.expanduser("~")

#subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None,
#               capture_output=False, shell=False, cwd=None, timeout=None,
#               check=False, encoding=None, errors=None, text=None, env=None,
#               universal_newlines=None, **other_popen_kwargs)

def insertInputs(zipfile, dbcfg, stdout, stderr=None):
    """parse e3sm input data and upload to pace database

    Parameters:
    zipfile(str): file path to a zipped e3sm data
    dbcfg(str): file path to a pace database configuration ascii data.
                Only one item should exist in a line in four lines in total::

                    username
                    password
                    hostname
                    databasename

    stdout(file object): output file object
    stderr(file object): error file object. Optional

    Returns:
    int: return code

    Notes:
    * As of this version, this function works if e3smlab is installed in Python 3.
      To make sure that e3smlab is installed in Python 3 env., user following command to install::

        python3 -m pip install e3smlab

    """

    import subprocess
    cmd = ["e3smlab", "pacedb", zipfile, "--db-cfg", dbcfg, "--create-expid-table", "--commit"]
    return subprocess.call(cmd, stdout=stdout, stderr=stderr)


def test_insert_inputs():


    dbcfg = os.path.join(home, "dbcfg2.txt")
    zipfile = "/data/pace-exp-files/exp-acmetest-130.zip"

    # run function
    ret = insertInputs(zipfile, dbcfg, sys.stdout, sys.stderr)

    # check if db exists
    #run e3smlab pacedb to verify

    assert ret == 0

#
#def test_print(capsys):
#
#    prj = E3SMlab()
#
#    cmd = "-- input @1 --forward '@x=2' -- print @x @data[0]"
#    ret, fwds = prj.run_command(cmd)
#
#    assert ret == 0
#
#    captured = capsys.readouterr()
#    assert captured.out == "21\n"
#    assert captured.err == ""
#
#
#def test_nml2json():
#
#    gzfile = os.path.join(here, "data.gz")
#    jsonfile = os.path.join(here, "data.json")
#
#    cmd = "nml2json %s -o %s" % (gzfile, jsonfile)
#
#    prj = E3SMlab()
#    ret, fwds = prj.run_command(cmd)
#
#    assert ret == 0
#    assert os.path.exists(jsonfile)
#
#    os.remove(jsonfile)
#
#
#def test_timestat():
#
#    timestat = os.path.join(here, "timestat")
#    jsonfile = os.path.join(here, "timestat.json")
#
#    cmd = "e3smtimestat %s -o %s" % (timestat, jsonfile)
#
#    prj = E3SMlab()
#    ret, fwds = prj.run_command(cmd)
#
#    assert ret == 0
#    assert os.path.exists(jsonfile)
#
#    os.remove(jsonfile)
#
##def test_inspectcompile(capsys):
##
##    e3smcasedir = "/global/homes/y/youngsun/scratch/e3smcase"
##
##    cmd = "inspectcompile %s" % e3smcasedir 
##
##    prj = E3SMlab()
##    ret, fwds = prj.run_command(cmd)
##
##    assert ret == 0
##
##    captured = capsys.readouterr()
##    assert captured.out == "test\n"
##    assert captured.err == ""
##
##    #assert os.path.exists(jsonfile)
##
##    #os.remove(jsonfile)
#
#
##def test_pacedb():
##
##    from pathlib import Path
##    from platform import node
##
##    expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
##    #expdata = "/data/pace-exp-files"
##    dbcfg = "%s/dbcfg.txt" % str(Path.home())
##
##    if node() != "e3sm" or not os.path.exists(expdata):
##        return
##
##    #/data/pace-exp-files/exp-ndkeen-20231.zip
##    #inputdir = "/data/pace-exp-files"
##
##    cmd = "pacedb %s %s" % (expdata, dbcfg)
##
##    prj = E3SMlab()
##    ret, fwds = prj.run_command(cmd)
##
##    assert ret == 0
##
#
##def test_pacedb_run_command():
##
##    from pathlib import Path
##    from platform import node
##
##    #expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
##    expdata = "/data/pace-exp-files"
##    dbcfg = "%s/dbcfg.txt" % str(Path.home())
##
##    if node() != "e3sm" or not os.path.exists(expdata):
##        return
##
##    #/data/pace-exp-files/exp-ndkeen-20231.zip
##    #inputdir = "/data/pace-exp-files"
##
##    cmd = ["pacedb", expdata, "--db-cfg", dbcfg, "--create-expid-table"]
##    lab = E3SMlab()
##    ret, fwds = lab.run_command(cmd)
##
##    assert ret == 0
#
#def test_pacedb_nml_table():
#
#    from pathlib import Path
#    from platform import node
#
#    expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
#    #expdata = "/data/pace-exp-files"
#    dbcfg = "%s/dbcfg.txt" % str(Path.home())
#    outfile = os.path.join(here, "table.txt")
#    #outfile = "/pace/assets/static/test/js/table.txt"
#
#    if node() != "e3sm" or not os.path.exists(expdata):
#        return
#
#    #/data/pace-exp-files/exp-ndkeen-20231.zip
#    #inputdir = "/data/pace-exp-files"
#
#
#
##    #cmd = ["pacedbnml", "24924", "24923", "24922", "24921", "24920", "24919", "24918", "24917", "24916", "24915", "-n", "atm_in", "--db-cfg", dbcfg, "-o", outfile]
##    #cmd = ["pacedbnml", "24924", "24923", "24922", "24921", "24920", "24919", "24918", "24917", "24916", "24915", "--db-cfg", dbcfg, "-o", outfile]
##    #cmd = ["pacedbnml", "24924", "24923", "--db-cfg", dbcfg, "-o", outfile, "-n", "atm_in", "lnd_in"]
##    cmd = ["pacedbnml", "130", "--db-cfg", dbcfg, "-o", outfile, "-n", "atm_in", "lnd_in"]
#    cmd = ["pacedbnml", "24924", "--db-cfg", dbcfg, "-o", outfile, "-n", "atm_in", "lnd_in", "ice_in", "user_nl_cam"]
##    #cmd = ["pacedbnml", "130", "--db-cfg", dbcfg, "-o", outfile]
##    #cmd = ["pacedbnml", "24924", "24923", "--db-cfg", dbcfg, "-o", outfile]
##    #cmd = ["pacedbnml", "24923", "--db-cfg", dbcfg, "-o", outfile]
##    cmd = ["pacedbnml", "24924", "--db-cfg", dbcfg, "-o", outfile]
#    lab = E3SMlab()
#    ret, fwds = lab.run_command(cmd)
#
#    assert ret == 0
#    assert os.path.isfile(outfile)
#
#    os.remove(outfile)
#
##def test_pacedb_table():
##
##    from pathlib import Path
##    from platform import node
##
##    expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
##    #expdata = "/data/pace-exp-files"
##    dbcfg = "%s/dbcfg.txt" % str(Path.home())
##    outfile = os.path.join(here, "table.txt")
##    #outfile = "/pace/assets/static/test/js/tablenmlxml.txt"
##
##    if node() != "e3sm" or not os.path.exists(expdata):
##        return
##
###    #cmd = ["pacedbnml", "24924", "24923", "24922", "24921", "24920", "24919", "24918", "24917", "24916", "24915", "-n", "atm_in", "--db-cfg", dbcfg, "-o", outfile]
###    cmd = ["pacedbtbl", "24924", "24923", "24922", "24921", "24920", "24919", "24918", "24917", "24916", "24915", "--db-cfg", dbcfg, "-o", outfile]
###    #cmd = ["pacedbnml", "24924", "24923", "--db-cfg", dbcfg, "-o", outfile, "-n", "atm_in", "lnd_in"]
###    cmd = ["pacedbnml", "130", "--db-cfg", dbcfg, "-o", outfile, "-n", "atm_in", "lnd_in"]
###    #cmd = ["pacedbnml", "130", "--db-cfg", dbcfg, "-o", outfile]
###    #cmd = ["pacedbnml", "24924", "24923", "--db-cfg", dbcfg, "-o", outfile]
###    #cmd = ["pacedbnml", "24923", "--db-cfg", dbcfg, "-o", outfile]
##    cmd = ["pacedbtbl", "24924", "--db-cfg", dbcfg, "-n", "atm_in", "-x", "env_case", "-o", outfile]
##    lab = E3SMlab()
##    ret, fwds = lab.run_command(cmd)
##
##    assert ret == 0
##    assert os.path.isfile(outfile)
##
##    os.remove(outfile)
