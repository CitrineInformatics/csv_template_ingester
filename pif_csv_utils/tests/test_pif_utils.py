# coding: utf-8
from pif_csv_utils.pif_utils import *
from pypif.obj import *


def test_add_uid():
    syst = add_uid(System(), '1./*2abcD345')
    assert syst.uid == '12abcD345'


def test_add_formula():
    syst = add_formula(ChemicalSystem(), 'NaCl')
    assert syst.chemical_formula == 'NaCl'


def test_add_name():
    syst = add_name(ChemicalSystem(), 'Sodium Chloride')
    assert syst.names[0] == 'Sodium Chloride'
    syst = add_name(syst, 'Salt')
    assert syst.names[0] == 'Sodium Chloride'
    assert syst.names[1] == 'Salt'


def test_add_method():
    syst = add_method(ChemicalSystem(properties=[Property(name='Band gap', scalars='12', units='eV')]), 'DFT')
    assert syst.properties[0].name == 'Band gap'
    assert syst.properties[0].methods[0].name == 'DFT'


def test_add_number():
    syst = add_number(ChemicalSystem(properties=[Property(name='Band gap', scalars='12', units='eV')]), '1', 'figure')
    assert syst.properties[0].name == 'Band gap'
    assert syst.properties[0].references[0].figure.number == '1'


def test_add_caption():
    syst = add_caption(ChemicalSystem(properties=[Property(name='Band gap', scalars='12', units='eV')]),
                       'This is a caption', 'figure')
    assert syst.properties[0].name == 'Band gap'
    assert syst.properties[0].references[0].figure.caption == 'This is a caption'


def test_add_datatype():
    syst = add_datatype(ChemicalSystem(properties=[Property(name='Band gap', scalars='12', units='eV')]),
                        'Computational')
    assert syst.properties[0].name == 'Band gap'
    assert syst.properties[0].data_type == 'Computational'


def test_add_preparation_step():
    syst = add_preparation_step(ChemicalSystem(), 'Annealing')
    assert syst.preparation[0].name == 'Annealing'


def test_format_main_prop():
    properties = format_main_prop([Property(name='Hardness', scalars='12'), Property(name='Strength', scalars='34')],
                                  [Value(name='Temperature', scalars='273', units='K')])
    assert properties[0].conditions[0].name == 'Temperature'
    assert properties[0].conditions[0].scalars == '273'
    assert properties[0].conditions[0].units == 'K'

    assert properties[1].conditions[0].name == 'Temperature'
    assert properties[1].conditions[0].scalars == '273'
    assert properties[1].conditions[0].units == 'K'


def test_property_merge():
    new_properties = property_merge(
        [Property(name='Hardness', scalars='12', units='HV'), Property(name='Hardness', scalars='120', units='HV'),
         Property(name='Hardness', scalars='1', units='HRC')])
    assert len(new_properties) == 2
