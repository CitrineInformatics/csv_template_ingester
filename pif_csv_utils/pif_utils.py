# coding: utf-8
from pypif.obj import *
from pif_csv_utils.general import *


def add_uid(systm, uid):
    """
    Adds a uid to a system

    :param systm: system object to add the uid to
    :param uid: uid to add
    :return: system updated with the uid info
    """

    if systm.uid:
        raise ValueError(
            'You are attempting to add a UID to a system that already has one. Each system can only have 1 UID.\n')
    elif isinstance(uid, list):
        raise ValueError('You are trying to add multiple UIDs to a system. Each ChemicalSystem can only have 1 UID')
    elif uid:
        systm.uid = re.sub(r'\W', '', uid)
        print ('UIDs manually added. If two systems have the same then one will be overwritten by the information in the other. Please make sure all UIDs are unique.')

    return systm


def add_formula(systm, formula):
    """
    Adds a formula to a ChemicalSystem

    :param systm: system object to add the name to
    :param formula: formula to add
    :return: system updated with the formula info
    """
    if not isinstance(systm, ChemicalSystem):
        raise TypeError('A chemical formula can only be added to a ChemicalSystem')

    if systm.chemical_formula:
        raise ValueError(
            'You are attempting to add a chemical formula to a system that already has one. Each ChemicalSystem can only have 1 formula.\n')
    elif isinstance(formula, list):
        raise ValueError('You are trying to add multiple formulas to a system. Each ChemicalSystem can only have 1 formula')
    elif formula:
        systm.chemical_formula = formula

    return systm


def add_name(systm, systm_name):
    """
    Adds a name to a system

    :param systm: system object to add the name to
    :param systm_name: name(s) to add
    :return: system updated with the name info
    """

    if systm_name and systm_name != '[]':
        systm_name = listify(systm_name)

        if systm.names:
            systm.names = listify(systm.names)
            systm.names.extend(systm_name)
        else:
            systm.names = systm_name

    return systm


def add_method(systm, method_value):
    """
    Adds a method to the last property in a system

    :param systm: system object to add the method to
    :param method_value: method name to add
    :return: system updated with the method info
    """

    if method_value:
        if systm.properties:
            prop = systm.properties[-1]
        else:
            raise ValueError(
                'Method details provided before a property was specified. Method columns must appear to the right of the property they belong to.\n')

        if prop.methods:
            prop.methods = listify(prop.methods)
        else:
            prop.methods = []

        new_method = Method()
        new_method.name = method_value

        prop.methods.append(new_method)

        systm.properties[-1] = prop

    return systm


def add_number(systm, number_value, source_type):
    """
    Adds a number to the last property in a system

    :param systm: system object to add the number to
    :param number_value: number to add
    :param source_type: table or figure
    :return: system updated with the number info
    """

    if number_value:
        if systm.properties:
            prop = systm.properties[-1]
        else:
            raise ValueError(
                'Number details provided before a property was specified. Number columns must appear to the right of the property they belong to.\n')

        if prop.references:
            prop.references = listify(prop.references)
        else:
            prop.references = [Reference()]

        if source_type == 'figure':
            if not prop.references[0].figure:
                prop.references[0].figure = DisplayItem()
            prop.references[0].figure.number = number_value
        else:
            if not prop.references[0].table:
                prop.references[0].table = DisplayItem()
            prop.references[0].table.number = number_value

        systm.properties[-1] = prop

    return systm


def add_caption(systm, caption_value, source_type):
    """
    Adds a method to the last property in a system
    :param systm: system object to add the method to
    :param caption_value: method name to add
    :param source_type: table or figure
    :return: system updated with the caption info
    """

    if caption_value:
        if systm.properties:
            prop = systm.properties[-1]
        else:
            raise ValueError(
                'Caption details provided before a property was specified. Caption columns must appear to the right of the property they belong to.\n')

        if prop.references:
            prop.references = listify(prop.references)
        else:
            prop.references = [Reference()]

        if source_type == 'figure':
            if not prop.references[0].figure:
                prop.references[0].figure = DisplayItem()
            prop.references[0].figure.caption = caption_value
        else:
            if not prop.references[0].table:
                prop.references[0].table = DisplayItem()
            prop.references[0].table.caption = caption_value

        systm.properties[-1] = prop

    return systm


def add_datatype(systm, datatype):
    """
    Adds a datatype to the last property in a system

    :param systm: system object to add the datatype to
    :param datatype: datatype to add
    :return: system updated with the datatype info
    """

    if datatype:

        if systm.properties:
            prop = systm.properties[-1]
        else:
            raise ValueError(
                'Data type provided before a property was specified. Data type columns must appear to the right of the property that they belong to.\n')

        prop.data_type = datatype

        systm.properties[-1] = prop

    return systm


def add_preparation_step(systm, preparation_step_name):
    """
    Adds a preparation step to a system

    :param systm: system object to add the preparation step to
    :param preparation_step_name: name of the preparation step
    :return: system updated with the preparation step info
    """

    step = ProcessStep()

    step.name = preparation_step_name

    if systm.preparation:
        systm.preparation = listify(systm.preparation)
        systm.preparation.append(step)
    else:
        systm.preparation = [step]

    return systm


def format_main_prop(properties, all_condition):
    """
    Format properties and add all_conditions to every property

    :param properties: list of property objects
    :param all_condition: list of condition objects
    :return: updated property list
    """

    properties = [prop for prop in properties if prop.scalars != [''] or prop.files]

    if all_condition:
        for prop in properties:
            if prop.conditions:
                prop.conditions = listify(prop.conditions)
                prop.conditions.extend(all_condition)
            else:
                prop.conditions = all_condition

    return properties


def property_merge(properties_list):
    """
    Merge properties in the properties list

    :param properties_list: list of properties to merge
    :return: Merged list of properties
    """

    prop_dict = create_prop_dictionary(properties_list)

    merged_properties = []
    for item in prop_dict:
        for i, p in enumerate(prop_dict[item]):
            if i == 0:
                if p.scalars:
                    if not isinstance(p.scalars, list):
                        p.scalars = [p.scalars]
                    if p.conditions:
                        for c in p.conditions:
                            if not isinstance(c.scalars, list):
                                c.scalars = [c.scalars]
                merged_properties.append(p)

            else:
                if p.scalars:
                    if not isinstance(p.scalars, list):
                        merged_properties[-1].scalars.append(p.scalars)
                    else:
                        merged_properties[-1].scalars.extend(p.scalars)
                    if p.conditions:
                        for j, c in enumerate(p.conditions):
                            if not isinstance(c.scalars, list):
                                merged_properties[-1].conditions[j].scalars.append(c.scalars)
                            else:
                                merged_properties[-1].conditions[j].scalars.extend(c.scalars)

    return merged_properties


def create_prop_dictionary(properties_list):
    """
    Creates a dictionary of all properties from the properties list

    :param properties_list: list of property objects
    :return: dictionary of property objects grouped by unique key (name, unit, condition name, condition unit, method and data type)
    """

    prop_dict = {}
    for prop in properties_list:

        identifier = prop.name + '-'
        if prop.units:
            identifier += prop.units + '-'
        else:
            identifier += '' + '-'
        if prop.conditions:
            for cond in prop.conditions:
                identifier += cond.name + '-'
                if cond.units:
                    identifier += cond.units
                else:
                    identifier += '' + '-'
        if prop.methods:
            for meth in prop.methods:
                identifier += meth.name + '-'
        if prop.data_type:
            identifier += prop.data_type + '-'

        if prop.scalars or prop.files:
            try:
                prop_dict[identifier].append(prop)
            except KeyError:
                prop_dict[identifier] = [prop]

    return prop_dict
