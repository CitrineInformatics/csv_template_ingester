# coding: utf-8
import sys
from pypif import pif
from pif_csv_utils.file_utils import *
from csv_template_ingester.template_csv_parser import *


def _check_table_size(table, cell_limit=100 * 100000 + 1):
    """
    Check a reader object to see if the total number of cells exceeds the set limit

    :param table: The reader object containing the table data
    :param cell_limit: Max number of cells allowed
    :return: True if within the limit or exits if the table is too large
    """

    pif_count = 0
    col_count = 0

    for i, row in enumerate(table):
        if i == 0:
            col_count = len(row)
        else:
            pif_count += 1

        if pif_count * col_count > cell_limit:
            raise ValueError(
                'This ingester only supports up to {} cells (rows * columns).\nPlease split your file into smaller files and ingest each separately'.format(
                    cell_limit))

    return True


def create_pif(headers, row):
    """
    Creates PIFs from lists of table row

    :param headers: header data from the table
    :param row: the row of data
    :return: ChemicalSystem containing the data from that row
    """

    sys_dict = {}
    keywords, names, units, systs = get_header_info(headers)

    sys_dict, all_condition = add_fields(keywords, names, units, systs, sys_dict, row)

    main_system = sys_dict['main']
    main_system.sub_systems = []

    if main_system.properties:
        main_system.properties = format_main_prop(main_system.properties, all_condition)

    if main_system.preparation:
        main_system.preparation = [step for step in main_system.preparation if step.name != '']

    for item in sys_dict:
        if item != 'main':
            if len(pif.dumps(sys_dict[item])):
                main_system.sub_systems.append(sys_dict[item])

    return main_system


def convert(files=[], **kwargs):
    """
    Converts a specialized CSV/TSV file to a physical information file.

    :param files: list of files to convert
    :return: yields PIFs created from the input files
    """

    for f in files:

        with open(f, 'rU') as input_file:
            if f.endswith('.csv'):
                table = get_data_from_csv(input_file)

            elif f.endswith('.tsv'):
                table = get_data_from_tsv(input_file)

            else:
                raise IOError('Filetype provided is not compatible with this parser. Please upload a .csv or .tsv file.\n')

            if not _check_table_size(table, (100 * 100000 + 1)):
                continue

            input_file.seek(0)

            for i, row in enumerate(table):

                if not any(row):
                    continue

                if i == 0:
                    headers = row
                else:
                    row_pif = create_pif(headers, row)

                    yield row_pif


if __name__ == '__main__':
    result = convert(files=[sys.argv[1]])

    with open(sys.argv[1].replace('.{}'.format(sys.argv[1].rpartition('.')[-1]), '-pif.json'), 'w') as output_file:
        pif.dump(list(result), output_file, indent=2)
