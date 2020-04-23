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
