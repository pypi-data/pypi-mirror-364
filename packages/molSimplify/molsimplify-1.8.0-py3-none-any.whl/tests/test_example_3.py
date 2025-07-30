import pytest
import helperFuncs as hp


@pytest.mark.skip("Skipping example 3 + FF as it is unclear to me if the core "
                  "should be frozen during the final optimization. RM")
def test_example_3(tmp_path, resource_path_root):
    testName = "example_3"
    threshMLBL = 0.1
    threshLG = 1.0
    threshOG = 2.0
    [passNumAtoms, passMLBL, passLG, passOG, pass_report, pass_qcin] = hp.runtest(
        tmp_path, resource_path_root, testName, threshMLBL, threshLG, threshOG)
    assert passNumAtoms
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report, pass_qcin


def test_example_3_No_FF(tmp_path, resource_path_root):
    testName = "example_3"
    threshMLBL = 0.1
    threshLG = 1.0
    threshOG = 2.0
    [passNumAtoms, passMLBL, passLG, passOG, pass_report, pass_qcin] = hp.runtestNoFF(
        tmp_path, resource_path_root, testName, threshMLBL, threshLG, threshOG)
    assert passNumAtoms
    assert passMLBL
    assert passLG
    assert passOG
    assert pass_report, pass_qcin
