# coding: utf-8
from pif_csv_utils.general import *
from pypif.obj import *


def test_normalize():
    string = normalize('This is a Test 123 *_-')
    assert string == 'thisisatest123_'


def test_listify():
    result = listify(Person())
    assert isinstance(result[0], Person)

    result_two = listify(None)
    assert result_two is None

    result_three = listify([Person()])
    assert isinstance(result_three[0], Person)
