# coding: utf-8
from pif_csv_utils.pif_utils import *
import csv
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def get_units(column_header):
    """
    Gets a unit from the header cell. Only match single parenthesis not double.

    :param column_header:  header cell
    :return: unit, updated column_header
    """

    if '((' in column_header and '))' in column_header and '\\' not in column_header:
        potential_unit = re.findall(r'(?<!\()\((?!\()(.*)(?<!\))\)(?!\))', column_header)
    elif '(' in column_header and ')' in column_header:
        potential_unit = re.findall(r'(?<!\\|\()(?:\()(.*)(?<!\\)(?:\))', column_header)
    else:
        potential_unit = None

    if potential_unit:
        unit = potential_unit[-1].replace('\(', '(').replace('\)', ')')
        column_header = column_header.replace('(' + potential_unit[-1] + ')', '').replace('\(', '(').replace('\)', ')')
        while '  ' in column_header:
            column_header = column_header.replace('  ', ' ')
        while '((' in column_header:
            column_header = column_header.replace('((', '(').replace('))', ')')
    else:
        unit = ''

    return unit, column_header.strip()


def split_on_keyword(string):
    """
    Split a string on a known keyword

    :param string: string to split
    :return: list of pieces
    """

    pieces = re.split(
            r'(name|formula|identifier|figurenumber|tablenumber|tablecaption|figurecaption|composition|processstep|processstepdetail|preparationstepdetail|method|datatype|file|idealcomposition|actualcomposition|reference|preparationstep|property|condition|idealquantity|actualquantity|classification)',
            normalize(string))

    return pieces


def get_keyword(column_header):
    """
    Gets a keyword from the header cell

    :param column_header: header cell
    :return: keyword, system the column should be associated with, updated column_header
    """

    if ':' in column_header:
        if column_header.count(':') > 2:
            raise ValueError(
                'Header cells should contain a maximum of one colon (:) to separate the keyword from the column name.\n')
        keyword = column_header.split(':')[0]
        column_header = column_header.split(':')[1]
    else:
        keyword = column_header
        column_header = column_header.replace(keyword, '').replace('  ', ' ')

    if 'system' in normalize(keyword):
        pieces = split_on_keyword(keyword)
        syst = pieces[0]
        keyword = pieces[1].strip()
    else:
        syst = 'main'

    return keyword, syst, column_header.strip()


def get_system(column_header):
    """
    Gets the system to which a column should be associated

    :param column_header: header cell
    :return: system the column should be associated with, updated column_header
    """

    if 'system' in normalize(column_header):
        pieces = split_on_keyword(column_header)
        syst = pieces[0]
        column_header = pieces[1].strip()

    else:
        syst = 'main'

    return syst, column_header.strip()


def get_header_info(headers):
    """
    Breaks headers into their components

    :param headers: list of header values
    :return: lists of keywords, names, units, systs
    """

    keywords = []
    names = []
    units = []
    systs = []

    for column_header in headers:
        column_header = decode_string(column_header)

        unit, column_header = get_units(column_header)
        units.append(unit)

        keyword, syst, column_header = get_keyword(column_header)
        keywords.append(keyword)
        systs.append(syst)

        names.append(column_header)

    return keywords, names, units, systs


def is_list(string):
    """
    Checks to see if a string contains a list in the form [A, B]

    :param string: string to evaluate
    :return: Boolean
    """

    if string:
        if '[' == string[0] and ']' == string[-1] and ',' in string:
            return True

    return False


def create_list(string):
    """
    Creates a list from a string of the form [A, B]

    :param string: string to convert to list
    :return: list
    """

    contents = csv.reader(StringIO(string[1:-1]), delimiter=',', quotechar='\"')

    lst = []
    for item in contents:
        lst.extend([val.strip() for val in item])

    return lst


def add_fields(keywords, names, units, systs, sys_dict, row):
    """
    Add the row data to a system and add that system to the sys_dict

    :param keywords: keywords from headers
    :param names: column names from headers
    :param units: units from headers
    :param systs: system names from headers
    :param sys_dict: dictionary of systems
    :param row: data for the current row
    :return: updated dictionary and list of all_conditions
    """

    for s in set(systs):
        sys_dict[s] = ChemicalSystem()

    all_condition = []

    unknown = ''

    for j, cell in enumerate(row):
        cell = decode_string(cell)

        if is_list(cell):
            cell = create_list(cell)

        systm = sys_dict[systs[j]]

        if 'formula' == normalize(keywords[j]):
            systm = add_formula(systm, cell)

        elif 'uid' == normalize(keywords[j]):
            systm = add_uid(systm, cell)

        elif 'name' == normalize(keywords[j]):
            systm = add_name(systm, cell)

        elif 'contact' == normalize(keywords[j]):
            systm = add_contacts(systm, cell, names, j)

        elif 'file' == normalize(keywords[j]):
            systm = add_newfile(systm, cell, names, j)

        elif 'identifier' == normalize(keywords[j]):
            systm = add_identifier(systm, cell, names, j)

        elif 'classification' == normalize(keywords[j]):
            systm = add_classification(systm, cell, names, j)

        elif 'property' == normalize(keywords[j]):
            systm = add_property(systm, cell, names, units, j)

        elif 'condition' == normalize(keywords[j]):
            systm = add_condition(systm, cell, names, units, j)

        elif 'allcondition' == normalize(keywords[j]):
            all_condition = add_all_condition(all_condition, cell, names, units, j)

        elif 'method' == normalize(keywords[j]):
            systm = add_method(systm, cell)

        elif 'figurenumber' == normalize(keywords[j]):
            systm = add_number(systm, cell, 'figure')

        elif 'figurecaption' == normalize(keywords[j]):
            systm = add_caption(systm, cell, 'figure')

        elif 'tablenumber' == normalize(keywords[j]):
            systm = add_number(systm, cell, 'table')

        elif 'tablecaption' == normalize(keywords[j]):
            systm = add_caption(systm, cell, 'table')

        elif 'datatype' == normalize(keywords[j]):
            systm = add_datatype(systm, cell)

        elif 'preparationstepname' == normalize(keywords[j]) or 'processstepname' == normalize(keywords[j]):
            systm = add_preparation_step(systm, cell)

        elif 'preparationstepdetail' == normalize(keywords[j]) or 'processstepdetail' == normalize(keywords[j]):
            systm = add_preparation_step_detail(systm, cell, names, units, j)

        elif 'reference' == normalize(keywords[j]):
            systm = add_reference(systm, cell, names, j)

        elif 'idealcomposition' == normalize(keywords[j]):
            systm = add_ideal_composition(systm, cell, names, units, j)

        elif 'composition' == normalize(keywords[j]):
            systm = add_ideal_composition(systm, cell, names, units, j)

        elif 'actualcomposition' == normalize(keywords[j]):
            systm = add_actual_composition(systm, cell, names, units, j)

        elif 'idealquantity' == normalize(keywords[j]):
            systm = add_ideal_quantity(systm, cell, units, j)

        elif 'actualquantity' == normalize(keywords[j]):
            systm = add_actual_quantity(systm, cell, units, j)

        else:
            unknown += ', %s' % j

    if any(unknown):
        print ('Unknown header(s) for column(s) %s.\n' % (unknown[1:]))

    return sys_dict, all_condition


def create_person(contact_value, names, column_index):
    """
    Creates a person object

    :param contact_value: value to use in the person object
    :param names: list of column names
    :param column_index: column index to reference
    :return: person object in a list
    """

    recognized_contact_fields = ['name', 'email', 'url']

    new_person = Person()

    if normalize(names[column_index]) in recognized_contact_fields:
        setattr(new_person, normalize(names[column_index]), contact_value)
    else:
        new_person.name = contact_value

    return [new_person]


def add_contacts(systm, contact_value, names, column_index):
    """
    Adds contact info to existing or new people objects

    :param systm: system to add to
    :param contact_value: value to add
    :param names: list of column names
    :param column_index: column index to reference
    :return: updated system with new contact info added
    """

    if contact_value:

        systm.contacts = listify(systm.contacts)

        if not systm.contacts:
            people = create_person(contact_value, names, column_index)

        elif len(systm.contacts) == 1:
            existing_person = systm.contacts[0]

            if getattr(existing_person, normalize(names[column_index])):
                new_person = create_person(contact_value, names, column_index)
            else:
                setattr(existing_person, normalize(names[column_index]), contact_value)
                new_person = None

            new_person = listify(new_person)
            existing_person = listify(existing_person)

            if new_person:
                people = existing_person + new_person
            else:
                people = existing_person

        elif len(systm.contacts) > 1:

            existing_people = systm.contacts[:-1]
            last_person = systm.contacts[-1]

            if getattr(last_person, normalize(names[column_index])):
                new_person = create_person(contact_value, names, column_index)
            else:
                setattr(last_person, normalize(names[column_index]), contact_value)
                new_person = None

            new_person = listify(new_person)
            last_person = listify(last_person)
            existing_people = listify(existing_people)

            if new_person:
                people = existing_people + last_person + new_person
            else:
                people = existing_people + last_person

        systm.contacts = people

    return systm


def add_actual_composition(systm, composition_value, names, units, column_index):
    """
    Adds an identifier to a system

    :param systm: system object to add the identifier to
    :param composition_value: composition info to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the identifier info
    """

    if composition_value:

        comp = Composition()

        if names[column_index]:
            comp.element = names[column_index]
        else:
            raise ValueError('No element has been specified in column: %s' % column_index)

        if 'atomic' in units[column_index] or 'at' in units[column_index]:
            comp.actual_atomic_percent = composition_value

        elif 'weight' in units[column_index] or 'wt' in units[column_index]:
            comp.actual_weight_percent = composition_value

        else:
            raise ValueError('Please specify atomic or weight percent for the composition in column: %s\n' % column_index)

        if systm.composition:
            systm.composition = listify(systm.composition)
            systm.composition.append(comp)
        else:
            systm.composition = [comp]

    return systm


def add_ideal_composition(systm, composition_value, names, units, column_index):
    """
    Adds an identifier to a system

    :param systm: system object to add the identifier to
    :param composition_value: composition info to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the identifier info
    """

    if composition_value:

        comp = Composition()

        if names[column_index]:
            comp.element = names[column_index]
        else:
            raise ValueError('No element has been specified in column: %s' % column_index)

        if 'atomic' in units[column_index] or 'at' in units[column_index]:
            comp.ideal_atomic_percent = composition_value

        elif 'weight' in units[column_index] or 'wt' in units[column_index]:
            comp.ideal_weight_percent = composition_value

        else:
            raise ValueError('Please specify atomic or weight percent for the composition in column: %s\n' % column_index)

        if systm.composition:
            systm.composition = listify(systm.composition)
            systm.composition.append(comp)
        else:
            systm.composition = [comp]

    return systm


def add_ideal_quantity(systm, quantity_value, units, column_index):
    """
    Adds an identifier to a system

    :param systm: system object to add the identifier to
    :param quantity_value: quantity info to add
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the identifier info
    """

    if quantity_value:

        quant = Quantity()

        if 'mass' in units[column_index] in units[column_index]:
            quant.ideal_mass_percent = Scalar(value=quantity_value)

        elif 'volume' in units[column_index] in units[column_index]:
            quant.ideal_volume_percent = Scalar(value=quantity_value)

        elif 'number' in units[column_index] in units[column_index]:
            quant.ideal_number_percent = Scalar(value=quantity_value)

        else:
            raise ValueError('Please specify mass, volume or number percent for the quantity in column: %s\n' % column_index)

        systm.quantity = quant

    return systm


def add_actual_quantity(systm, quantity_value, units, column_index):
    """
    Adds an identifier to a system

    :param systm: system object to add the identifier to
    :param quantity_value: quantity info to add
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the identifier info
    """

    if quantity_value:

        quant = Quantity()

        if 'mass' in units[column_index] in units[column_index]:
            quant.actual_mass_percent = Scalar(value=quantity_value)

        elif 'volume' in units[column_index] in units[column_index]:
            quant.actual_volume_percent = Scalar(value=quantity_value)

        elif 'number' in units[column_index] in units[column_index]:
            quant.actual_number_percent = Scalar(value=quantity_value)

        else:
            raise ValueError('Please specify mass, volume or number percent for the quantity in column: %s\n' % column_index)

        systm.quantity = quant

    return systm


def add_newfile(systm, file_name, names, column_index):
    """
    Adds a file reference to the last property in a system

    :param systm: system object to add the property to
    :param file_name: name of the file
    :param names: list of names from the header row
    :param column_index: index of the current column
    :return: system updated with file info
    """

    prop = Property()
    if names[column_index]:
        prop.name = names[column_index]
    else:
        raise ValueError(
            'No file name has been specified for column: %s. Every files column must have a name provided in the header row.\n' % (
                column_index + 1))

    ext = file_name.split('.')[-1]
    if file_name:
        if ext.lower() in ['tif', 'jpg', 'png']:
            mt = 'image'
        else:
            mt = 'file'
        prop.files = [FileReference(relative_path=file_name, mimeType='%s/%s' % (mt, ext))]

        if systm.properties:
            systm.properties.append(prop)
        else:
            systm.properties = [prop]

    return systm


def add_property(systm, property_value, names, units, column_index):
    """
    Adds a property to a system

    :param systm: system object to add the property to
    :param property_value: property to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the property info
    """

    prop = Property()
    if names[column_index]:
        prop.name = names[column_index]
    else:
        raise ValueError(
            'No property name has been specified for column: %s. Every property column must have a name provided in the header row.\n' % (
                column_index + 1))

    if not property_value:
        return systm

    property_value = listify(property_value)
    prop.scalars = property_value

    if units[column_index]:
        prop.units = units[column_index]

    if systm.properties:
        systm.properties.append(prop)
    else:
        systm.properties = [prop]

    return systm


def add_preparation_step_detail(systm, preparation_step_detail, names, units, column_index):
    """
    Adds a detail to the last preparation step in a system

    :param systm: system object to add the detail to
    :param preparation_step_detail: detail to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the detail info
    """

    if preparation_step_detail:
        if systm.preparation:
            step = systm.preparation[-1]
        else:
            raise ValueError(
                'Preparation details were provided before a step name was given. A preparation step name must always be provided to the left of the details columns.\n')

        if step.details:
            step.details = listify(step.details)
        else:
            step.details = []

        detail = Value()
        if names[column_index]:
            detail.name = names[column_index]
        else:
            raise ValueError(
                'No preparation step detail name has been specified for column: %s. Preparation step details mst have a name specified in the header row.\n' % (
                    column_index + 1))

        preparation_step_detail = listify(preparation_step_detail)
        detail.scalars = preparation_step_detail

        if units[column_index]:
            detail.units = units[column_index]

        step.details.append(detail)

        systm.preparation[-1] = step

    return systm


def add_condition(systm, condition, names, units, column_index):
    """
    Adds a condition to the last property in a system

    :param systm: system object to add the condition to
    :param condition: condition to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the condition info
    """

    if condition:
        if systm.properties:
            prop = systm.properties[-1]
        else:
            raise ValueError(
                'Condition details were provided before a property was given. Condition columns must appear to the right of the property that they belong to.\n')

        if prop.conditions:
            prop.conditions = listify(prop.conditions)
        else:
            prop.conditions = []

        conditions = Value()
        if names[column_index]:
            conditions.name = names[column_index]
        else:
            raise ValueError(
                'No condition name has been specified for column: %s. Conditions must have a name specified in the header row.\n' % (
                    column_index + 1))

        condition = listify(condition)
        conditions.scalars = condition

        if units[column_index]:
            conditions.units = units[column_index]

        prop.conditions.append(conditions)

        systm.properties[-1] = prop

    return systm


def add_all_condition(all_condition, condition, names, units, column_index):
    """
    Adds a condition to an array

    :param all_condition: list of all_conditions
    :param condition: condition to add
    :param names: list of names from the header row
    :param units: list of units from the header row
    :param column_index: index of the current column
    :return: system updated with the condition info
    """

    if condition:
        conditions = Value()
        if names[column_index]:
            conditions.name = names[column_index]

        condition = listify(condition)
        conditions.scalars = condition

        if units[column_index]:
            conditions.units = units[column_index]

        all_condition.append(conditions)

    return all_condition


def add_reference(systm, reference_value, names, column_index):
    """
    A reference to add to the system

    :param systm: system object to add the reference info to
    :param reference_value: reference value to add
    :param names: list of names from the header row
    :param column_index: index of the current column
    :return: system updated with the reference info
    """

    recognized_ref_fields = ['doi', 'isbn', 'publisher', 'title', 'year', 'journal', 'volume']

    if reference_value:

        systm.references = listify(systm.references)

        if not systm.references:
            r = Reference()

            if normalize(names[column_index]) in recognized_ref_fields:
                setattr(r, normalize(names[column_index]), reference_value)

            else:
                r.citation = reference_value

            r = [r]

        elif len(systm.references) == 1:
            new_reference = Reference()

            r = systm.references[0]

            if normalize(names[column_index]) in recognized_ref_fields:
                if not getattr(r, normalize(names[column_index])):
                    setattr(r, normalize(names[column_index]), reference_value)
                else:
                    setattr(new_reference, normalize(names[column_index]), reference_value)

            if new_reference:
                r = [r, new_reference]
            else:
                r = [r]

        elif len(systm.references) > 1:
            new_reference = Reference()

            rr = systm.references[:]

            existing_references = rr[:-1]
            ref = rr[-1]

            if normalize(names[column_index]) in recognized_ref_fields:

                if not getattr(ref, normalize(names[column_index])):
                    setattr(ref, normalize(names[column_index]), reference_value)
                else:
                    setattr(new_reference, normalize(names[column_index]), reference_value)

            if new_reference:
                r = existing_references + [ref] + [new_reference]
            else:
                r = existing_references + [ref]

        systm.references = r

    return systm


def add_identifier(systm, identifier, names, column_index):
    """
    Adds an ID to a system

    :param systm: system to update
    :param identifier: identifier to add
    :param names: list of names of the columns
    :param column_index: index of the column to use
    :return: updated system with identifier info
    """

    if identifier:

        ident = Id()
        if names[column_index]:
            ident.name = names[column_index]
        else:
            ident.name = 'ID'

        ident.value = identifier

        if systm.ids:
            systm.ids = listify(systm.ids)
            systm.ids.append(ident)
        else:
            systm.ids = [ident]

    return systm


def add_classification(systm, classification, names, column_index):
    """
    Adds an ID to a system

    :param systm: system to update
    :param classification: classification to add
    :param names: list of names of the columns
    :param column_index: index of the column to use
    :return: updated system with classification info
    """

    if classification:

        clss = Classification()
        if names[column_index]:
            clss.name = names[column_index]
        else:
            clss.name = 'Classification'

        clss.value = classification

        if systm.classifications:
            systm.classifications = listify(systm.classifications)
            systm.classifications.append(clss)
        else:
            systm.classifications = [clss]

    return systm
