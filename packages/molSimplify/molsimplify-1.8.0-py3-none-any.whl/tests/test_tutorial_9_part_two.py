import helperFuncs as hp


def test_tutorial_09_part_two(tmp_path, resource_path_root):
    testName = "tutorial_09_part_two"
    threshMLBL = 0.1
    threshLG = 2.0
    threshOG = 2.0
    [passNumAtoms, passMLBL, passLG, passOG, pass_report, pass_qcin] = hp.runtest(
        tmp_path, resource_path_root, testName, threshMLBL, threshLG, threshOG)
    assert passNumAtoms
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report
