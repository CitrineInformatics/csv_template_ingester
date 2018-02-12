# coding: utf-8
import csv


def get_data_from_csv(csv_file):
    """
    Get the data from a CSV file
    :param csv_file: open csv file
    :return: list of table data
    """

    # rough check for tab separated files
    if '\t' in csv_file.readline() and ',' not in csv_file.readline():
        csv_file.seek(0)
        reader = csv.reader(csv_file, delimiter='\t', quotechar='\"')
    else:
        csv_file.seek(0)
        reader = csv.reader(csv_file, delimiter=',', quotechar='\"')

    return reader


def get_data_from_tsv(tsv_file):
    """
    Get the data from a TSV file
    :param tsv_file: open tsv file
    :return: list of table data
    """

    return csv.reader(tsv_file, delimiter='\t', quotechar='\"')
