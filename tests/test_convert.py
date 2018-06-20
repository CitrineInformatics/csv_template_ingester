# coding: utf-8
from csv_template_ingester.converter import convert


def test_convert():
    pifs = list(convert(["./test_files/template_example.csv"]))
    assert pifs[0].names[0] == 'P20 Tool steel'
    assert pifs[0].sub_systems[0].names[0] == 'Martensite'
    assert pifs[0].classifications[0].name == 'Test Classification'
    assert pifs[0].classifications[0].value == 'Solvent'
    assert pifs[0].sub_systems[0].quantity.ideal_mass_percent.value == '80'
    assert pifs[0].contacts[0].name == 'Jo Hill'
    assert pifs[0].contacts[0].email == 'jo@citrine.io'
    assert pifs[0].contacts[2].name == 'Mary'
    assert pifs[0].contacts[2].url == 'http://jo'

    pifs_two = list(convert(["./test_files/template_example_two.csv"]))
    assert pifs_two[0].properties[2].name == 'SMILES'
    assert pifs_two[0].properties[2].scalars[0] == '[C]'
    assert pifs_two[0].names[1] == 'Sample 1'
    assert len(pifs_two[0].properties) == 3
    assert pifs_two[0].properties[1].name == 'Strength (Tensile)'
    assert pifs_two[0].properties[1].scalars[0] == '456'
