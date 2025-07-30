import pytest
import json
import numpy as np
import pandas as pd
from molSimplify.Informatics.MOF.MOF_descriptors import get_MOF_descriptors
from molSimplify.utils.timer import DebugTimer


@pytest.fixture
def ref_names():
    def RACs_names(depth=3, Gval=True):

        def generate_names(starts, properties, depth, scope="all"):
            names = []
            for start in starts:
                for prop in properties:
                    for d in range(depth + 1):
                        if scope is None:
                            names.append(f"{start}-{prop}-{d}")
                        else:
                            names.append(f"{start}-{prop}-{d}-{scope}")
            return names

        properties = ["chi", "Z", "I", "T", "S"]
        if Gval:
            properties.append("Gval")

        names = generate_names(["f-sbu", "mc", "D_mc"], properties, depth, scope=None)
        # f-link does not include the "scope"
        names.extend(generate_names(["f-link"], properties, depth, scope=None))

        properties.append("alpha")
        names.extend(
            generate_names(["lc", "D_lc", "func", "D_func"], properties, depth, scope=None))
        return names
    return RACs_names


def helper_RAC_check(resource_path_root, tmp_path, name, ref_names, Gval=False):
    with DebugTimer("get_MOF_descriptors()"):
        full_names, full_descriptors = get_MOF_descriptors(
            str(resource_path_root / "inputs" / "cif_files" / f"{name}.cif"),
            depth=3,
            path=str(tmp_path),
            xyz_path=str(tmp_path / "test.xyz"),
            Gval=Gval,
        )

    with open(resource_path_root / "refs" / "informatics" / "mof"  / "MOF_descriptors"
              / name / f"{name}.json", "r") as fin:
        ref = json.load(fin)

    assert full_names == ref_names(Gval=Gval)
    assert full_names == ref["names"]
    np.testing.assert_allclose(full_descriptors, ref["descriptors"], atol=1e-6)

    link_descriptors = pd.read_csv(tmp_path / "linker_descriptors.csv")
    link_ref = pd.read_csv(resource_path_root / "refs" / "informatics" / "mof" / "MOF_descriptors" / name / "linker_descriptors.csv")
    assert all(link_descriptors == link_ref)

    lc_descriptors = pd.read_csv(tmp_path / "lc_descriptors.csv")
    lc_ref = pd.read_csv(resource_path_root / "refs" / "informatics" / "mof" / "MOF_descriptors" / name / "lc_descriptors.csv")
    assert all(lc_descriptors == lc_ref)

    sbu_descriptors = pd.read_csv(tmp_path / "sbu_descriptors.csv")
    sbu_ref = pd.read_csv(resource_path_root / "refs" / "informatics" / "mof" / "MOF_descriptors" / name / "sbu_descriptors.csv")
    assert all(sbu_descriptors == sbu_ref)


@pytest.mark.parametrize(
    "name",
    [
        "odac-21383",
        "odac-21433",
        "odac-21478",
        "odac-21735",
        "odac-21816",
    ])
def test_get_MOF_descriptors_ODAC(resource_path_root, tmp_path, name, ref_names):
    # NOTE All the .cif files were converted to primitive unit cell using the
    # MOF_descriptors.get_primitive() function

    helper_RAC_check(resource_path_root, tmp_path, name, ref_names, Gval=True)


@pytest.mark.parametrize(
    "name",
    [
        "FOKYIP_clean",
        "SETDUS_clean",
        "UXUPEK_clean",
        "NEXXIZ_clean",
        "ETECIR_clean",
        "FAVGUH_clean",
        "YICDAR_clean",
        "VONBIK_clean",
    ])
def test_get_MOF_descriptors_JACS(resource_path_root, tmp_path, name, ref_names):
    """
    Tests a handful of the MOFs used in
    Nandy et al., J. Am. Chem. Soc. 2021, 143, 42, 17535-17547
    https://doi.org/10.1021/jacs.1c07217
    """
    # NOTE All the .cif files were converted to primitive unit cell using the
    # MOF_descriptors.get_primitive() function

    helper_RAC_check(resource_path_root, tmp_path, name, ref_names, Gval=False)


@pytest.mark.parametrize(
    "name",
    [
        "TIRLIQ",
        "YAHPON",
    ])
def test_get_MOF_descriptors_ligand_containing(resource_path_root, tmp_path, name, ref_names):
    # These MOFs contain pyridine and oxygen ligands attached to metals, respectively.

    helper_RAC_check(resource_path_root, tmp_path, name, ref_names, Gval=False)


@pytest.mark.parametrize(
    "name",
    [
        "odac-21383",
        "odac-21478",
        "odac-21816",
        "SETDUS_clean",
        "NEXXIZ_clean",
        "YICDAR_clean",
        "TIRLIQ",
    ])
def test_get_MOF_descriptors_non_trivial(resource_path_root, tmp_path, name, ref_names):
    with DebugTimer("get_MOF_descriptors()"):
        full_names, full_descriptors = get_MOF_descriptors(
            str(resource_path_root / "inputs" / "cif_files" / f"{name}.cif"),
            depth=3,
            path=str(tmp_path),
            xyz_path=str(tmp_path / "test.xyz"),
            Gval=name.startswith('odac'),
            non_trivial=True,
        )

    # Reference, obtained with non_trivial = False
    with open(resource_path_root / "refs" / "informatics" / "mof"  / "MOF_descriptors"
          / name / f"{name}.json", "r") as fin:
        ref = json.load(fin)

    set_1 = set(full_names)
    set_2 = set(ref['names'])
    assert set_1.issubset(set_2)
    assert len(set_1) < len(set_2)
    extra_names = set_2.difference(set_1)
    assert all(i.startswith('D') and ('-0' in i or '-I-' in i) for i in extra_names)

    dict_1 = dict(zip(full_names, full_descriptors))
    dict_2 = dict(zip(ref['names'], ref['descriptors']))
    assert all(dict_1[i] == dict_2[i] for i in full_names)
