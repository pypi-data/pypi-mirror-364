import helperFuncs as hp


def test_orca_ccsdt(tmp_path, resource_path_root):
    testName = "orca_ccsdt"
    threshMLBL = 0.1
    threshLG = 1.0
    threshOG = 8.0
    [passNumAtoms, passMLBL, passLG, passOG, pass_report, pass_qcin] = hp.runtest(
        tmp_path, resource_path_root, testName, threshMLBL, threshLG, threshOG)
    assert passNumAtoms
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report
