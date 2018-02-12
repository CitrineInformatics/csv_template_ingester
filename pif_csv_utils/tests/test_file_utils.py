# coding: utf-8
from pif_csv_utils.file_utils import *


def test_get_data_from_csv():
    with open("./test_files/template_example.csv", 'rU') as input_file:
        data = get_data_from_csv(input_file)
        for i, row in enumerate(data):
            if i == 0:
                assert row[0] == 'NAME:'


def test_get_data_from_tsv():
    with open("./test_files/template_example_tsv.tsv", 'rU') as input_file:
        data = get_data_from_csv(input_file)
        for i, row in enumerate(data):
            if i == 0:
                assert row[0] == 'NAME:'
