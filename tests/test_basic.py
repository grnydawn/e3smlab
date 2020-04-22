from e3smlab import E3SMLab

import os

here = os.path.dirname(os.path.abspath(__file__))
gzfile = os.path.join(here, "data.gz")
jsonfile = os.path.join(here, "data.json")


def test_basic():

    prj = E3SMLab()

    cmd = "input @1 --forward '@x=2'"
    ret = prj.main(cmd)

    assert ret == 0

def test_print(capsys):

    prj = E3SMLab()

    cmd = "-- input @1 --forward '@x=2' -- print @x @data[0]"
    ret = prj.main(cmd)

    assert ret == 0

    captured = capsys.readouterr()
    assert captured.out == "21\n"
    assert captured.err == ""

def test_nml2json():

    prj = E3SMLab()

    cmd = "nml2json %s -o %s" % (gzfile, jsonfile)
    ret = prj.main(cmd)

    assert ret == 0
    assert os.path.exists(jsonfile)

    os.remove(jsonfile)
