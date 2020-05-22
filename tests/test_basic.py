from e3smlab import E3SMlab

import os

here = os.path.dirname(os.path.abspath(__file__))


def test_basic():

    prj = E3SMlab()

    cmd = "input @1 --forward '@x=2'"
    ret = prj.main(cmd)

    assert ret == 0


def test_print(capsys):

    prj = E3SMlab()

    cmd = "-- input @1 --forward '@x=2' -- print @x @data[0]"
    ret = prj.main(cmd)

    assert ret == 0

    captured = capsys.readouterr()
    assert captured.out == "21\n"
    assert captured.err == ""


def test_nml2json():

    gzfile = os.path.join(here, "data.gz")
    jsonfile = os.path.join(here, "data.json")

    cmd = "nml2json %s -o %s" % (gzfile, jsonfile)

    prj = E3SMlab()
    ret = prj.main(cmd)

    assert ret == 0
    assert os.path.exists(jsonfile)

    os.remove(jsonfile)


def test_timestat():

    timestat = os.path.join(here, "timestat")
    jsonfile = os.path.join(here, "timestat.json")

    cmd = "e3smtimestat %s -o %s" % (timestat, jsonfile)

    prj = E3SMlab()
    ret = prj.main(cmd)

    assert ret == 0
    assert os.path.exists(jsonfile)

    os.remove(jsonfile)

#def test_inspectcompile(capsys):
#
#    e3smcasedir = "/global/homes/y/youngsun/scratch/e3smcase"
#
#    cmd = "inspectcompile %s" % e3smcasedir 
#
#    prj = E3SMlab()
#    ret = prj.main(cmd)
#
#    assert ret == 0
#
#    captured = capsys.readouterr()
#    assert captured.out == "test\n"
#    assert captured.err == ""
#
#    #assert os.path.exists(jsonfile)
#
#    #os.remove(jsonfile)


#def test_pacedb():
#
#    from pathlib import Path
#    from platform import node
#
#    expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
#    #expdata = "/data/pace-exp-files"
#    dbcfg = "%s/dbcfg.txt" % str(Path.home())
#
#    if node() != "e3sm" or not os.path.exists(expdata):
#        return
#
#    #/data/pace-exp-files/exp-ndkeen-20231.zip
#    #inputdir = "/data/pace-exp-files"
#
#    cmd = "pacedb %s %s" % (expdata, dbcfg)
#
#    prj = E3SMlab()
#    ret = prj.main(cmd)
#
#    assert ret == 0
#

#def test_pacedb_run_command():
#
#    from pathlib import Path
#    from platform import node
#
#    #expdata = "/data/pace-exp-files/exp-acmetest-130.zip"
#    expdata = "/data/pace-exp-files"
#    dbcfg = "%s/dbcfg.txt" % str(Path.home())
#
#    if node() != "e3sm" or not os.path.exists(expdata):
#        return
#
#    #/data/pace-exp-files/exp-ndkeen-20231.zip
#    #inputdir = "/data/pace-exp-files"
#
#    cmd = ["pacedb", expdata, "--db-cfg", dbcfg, "--create-expid-table"]
#    lab = E3SMlab()
#    ret, fwds = lab.run_command(cmd)
#
#    assert ret == 0
