from csv_template_ingester.template_csv_parser import *
from pypif.obj import *
import pytest


def test_get_units():
    # test legacy simple (()) non units
    units, column_header = get_units('Property name (units) ((test))')
    assert units == 'units'
    assert column_header == 'Property name (test)'

    # test new escaped parenthesis unit extraction
    units_two, column_header_two = get_units('Property name (A/B^\(C-\(D+E\)\))')
    assert units_two == 'A/B^(C-(D+E))'
    assert column_header_two == 'Property name'


def test_get_keyword():
    keyword, syst, column_header = get_keyword('PROPERTY: Test name (MPa)')
    assert keyword == 'PROPERTY'
    assert column_header == 'Test name (MPa)'

    keyword_two, syst_two, column_header_two = get_keyword('NAME')
    assert keyword_two == 'NAME'
    assert column_header_two == ''

def test_get_keyword_colon_count():
    """
    Tests the expected ValueError for >2 colons in the header.
    Test fails if ValueError not thrown
    """
    try:
        keyword, syst, column_header = get_keyword('PROPERTY::: Test name (MPa)')
    except ValueError:
        pass
    else:
        assert False, "ValueError was not raised"

def test_get_system():
    syst, column_header = get_system('SYSTEM A PROPERTY: Hardness (HV)')
    assert syst == 'systema'

    syst_two, column_header_two = get_system('PROPERTY: Hardness (HV)')
    assert syst_two == 'main'


def test_split_on_keyword():
    pieces = split_on_keyword('SUBSYSTEM A PROPERTY: Hardness (HV)')
    assert len(pieces) == 3
    assert pieces[0] == 'subsystema'
    pieces_two = split_on_keyword('SUBSYSTEM 1')
    assert len(pieces_two) == 1
    pieces_three = split_on_keyword('SUBSYSTEM ABCD PROCESS STEP')
    assert len(pieces_three) == 3
    assert pieces_three[1] == 'processstep'


def test_add_contacts():
    syst = add_contacts(ChemicalSystem(), 'Joanne Hill', ['name', 'url'], 0)
    assert syst.contacts[0].name == 'Joanne Hill'
    syst = add_contacts(syst, 'http://test', ['name', 'url'], 1)
    assert syst.contacts[0].url == 'http://test'
    syst = add_contacts(syst, 'jo2@email', ['name', 'email'], 1)
    assert syst.contacts[0].email == 'jo2@email'
    syst = add_contacts(syst, 'Jo Jo', ['name', 'email'], 0)
    assert syst.contacts[0].name == 'Joanne Hill'
    assert syst.contacts[1].name == 'Jo Jo'


def test_add_actual_composition():
    syst = add_actual_composition(ChemicalSystem(), '12', ['Fe', 'Cu'], ['wt%', 'at%'], 0)
    assert syst.composition[0].element == 'Fe'
    assert syst.composition[0].actual_weight_percent == '12'
    syst = add_actual_composition(syst, '20', ['Fe', 'Cu'], ['wt%', 'at%'], 1)
    assert syst.composition[1].element == 'Cu'
    assert syst.composition[1].actual_atomic_percent == '20'


def test_add_ideal_composition():
    syst = add_ideal_composition(ChemicalSystem(), '12', ['Fe', 'Cu'], ['wt%', 'at%'], 0)
    assert syst.composition[0].element == 'Fe'
    assert syst.composition[0].ideal_weight_percent == '12'
    syst = add_ideal_composition(syst, '20', ['Fe', 'Cu'], ['wt%', 'at%'], 1)
    assert syst.composition[1].element == 'Cu'
    assert syst.composition[1].ideal_atomic_percent == '20'


def test_add_ideal_quantity():
    syst = add_ideal_quantity(ChemicalSystem(), '12', ['mass%', 'volume%'], 0)
    assert syst.quantity.ideal_mass_percent.value == '12'
    syst = add_ideal_quantity(syst, '20', ['mass%', 'volume%'], 1)
    assert syst.quantity.ideal_volume_percent.value == '20'


def test_add_actual_quantity():
    syst = add_actual_quantity(ChemicalSystem(), '12', ['mass%', 'volume%'], 0)
    assert syst.quantity.actual_mass_percent.value == '12'
    syst = add_actual_quantity(syst, '20', ['mass%', 'volume%'], 1)
    assert syst.quantity.actual_volume_percent.value == '20'


def test_add_condition():
    syst = add_condition(ChemicalSystem(properties=[Property(name='Hardness', scalars='21', units='HV')]), '273',
                         ['Temperature'], ['K'], 0)
    assert syst.properties[0].name == 'Hardness'
    assert syst.properties[0].conditions[0].name == 'Temperature'
    assert syst.properties[0].conditions[0].scalars == ['273']
    assert syst.properties[0].conditions[0].units == 'K'


def test_add_reference():
    syst = add_reference(ChemicalSystem(), '10.10101', ['doi'], 0)
    syst = add_reference(syst, 'Test title', ['title'], 0)
    syst = add_reference(syst, '10.10102', ['doi'], 0)

    assert syst.references[0].doi == '10.10101'
    assert syst.references[0].title == 'Test title'
    assert syst.references[1].doi == '10.10102'


def test_get_header_info():
    keywords, names, units, systs = get_header_info(['IDENTIFIER', 'PROPERTY: Hardness (HV)'])
    assert keywords[0] == 'IDENTIFIER'
    assert names[1] == 'Hardness'
    assert units[0] == ''
    assert systs[1] == 'main'


def test_add_fields():
    sys_dict, all_condition = add_fields(['IDENTIFIER', 'PROPERTY'], ['', 'Hardness'], ['', 'HV'], ['main', 'main'], {},
                                         ['1234', '12'])
    assert all_condition == []
    assert len(sys_dict) == 1


def test_add_all_condition():
    all_conditions = add_all_condition([], '273', ['Temperature'], ['K'], 0)
    assert all_conditions[0].name == 'Temperature'
    assert all_conditions[0].scalars == ['273']
    assert all_conditions[0].units == 'K'


def test_add_newfile():
    syst = add_newfile(ChemicalSystem(), 'testfile.csv', ['Filename'], 0)
    assert syst.properties[0].files[0].mimeType == 'file/csv'
    assert syst.properties[0].files[0].relative_path == 'testfile.csv'
    assert syst.properties[0].name == 'Filename'

    syst_two = add_newfile(ChemicalSystem(), 'testfile.png', ['Filename'], 0)
    assert syst_two.properties[0].files[0].mimeType == 'image/png'
    assert syst_two.properties[0].files[0].relative_path == 'testfile.png'
    assert syst_two.properties[0].name == 'Filename'


def test_add_property():
    syst = add_property(ChemicalSystem(), '1200', ['Hardness'], ['HV'], 0)
    assert syst.properties[0].name == 'Hardness'
    assert syst.properties[0].scalars == ['1200']
    assert syst.properties[0].units == 'HV'

    syst = add_property(ChemicalSystem(), 'range(+140, 165)', ['Melting Temperature'], ['degC'], 0)
    assert syst.properties[0].name == 'Melting Temperature'
    assert syst.properties[0].scalars.minimum == 140
    assert syst.properties[0].scalars.maximum == 165
    assert syst.properties[0].units == 'degC'

    syst = add_property(ChemicalSystem(), 'range(0.140E+3, 16500E-2)', ['Melting Temperature'], ['degC'], 0)
    assert syst.properties[0].name == 'Melting Temperature'
    assert syst.properties[0].scalars.minimum == 140
    assert syst.properties[0].scalars.maximum == 165
    assert syst.properties[0].units == 'degC'

    syst = add_property(ChemicalSystem(), 'range(-.165E3, -14000E-2)', ['Melting Temperature'], ['degC'], 0)
    assert syst.properties[0].name == 'Melting Temperature'
    assert syst.properties[0].scalars.minimum == -165
    assert syst.properties[0].scalars.maximum == -140
    assert syst.properties[0].units == 'degC'

    with pytest.raises(ValueError):
        add_property(ChemicalSystem(), 'range(+.165E3, -14000E-2)', ['Melting Temperature'], ['degC'], 0)


def test_create_person():
    new_person = create_person('Jo Hill', ['name'], 0)
    assert new_person[0].name == 'Jo Hill'


def test_create_prop_dictionary():
    dict = create_prop_dictionary(
        [Property(name='Hardness', scalars='12', units='HV'), Property(name='Hardness', scalars='120', units='HV'),
         Property(name='Hardness', scalars='1', units='HRC')])
    assert len(dict) == 2


def test_add_identifier():
    syst = add_identifier(ChemicalSystem(), '1234', ['', 'ID2'], 0)
    syst = add_identifier(syst, '5678', ['', 'ID2'], 1)
    assert syst.ids[0].value == '1234'
    assert syst.ids[1].name == 'ID2'
    assert syst.ids[1].value == '5678'


def test_add_classification():
    syst = add_classification(ChemicalSystem(), '1234', ['', 'Class2'], 0)
    syst = add_classification(syst, '5678', ['', 'Class2'], 1)
    assert syst.classifications[0].value == '1234'
    assert syst.classifications[1].name == 'Class2'
    assert syst.classifications[1].value == '5678'


def test_add_preparation_step_detail():
    syst = add_preparation_step_detail(ChemicalSystem(preparation=[ProcessStep(name='Annealing')]), '1200',
                                       ['Temperature'], ['K'], 0)
    assert syst.preparation[0].name == 'Annealing'
    assert syst.preparation[0].details[0].name == 'Temperature'
    assert syst.preparation[0].details[0].scalars == ['1200']
    assert syst.preparation[0].details[0].units == 'K'


def test_is_list():
    assert is_list("[1, 2, 3, 4]") is True
    assert is_list("[1]") is False
    assert is_list("[Sample 1, Sample 2]") is True


def test_create_list():
    lst = create_list('[1, 2, 3, 4]')
    assert len(lst) == 4
    assert lst[1] == '2'