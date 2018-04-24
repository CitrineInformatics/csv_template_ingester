import re
import sys


def normalize(string):
    """
    Normalizes a string for comparison

    :param string: string to normalize
    :return: normalized string
    """

    normalized_string = re.sub(r'[\W\s]', '', string).lower()

    return normalized_string


def listify(item):
    """
    Check if an item is enclosed in a list and make it a list if not

    :param item: item to convert to a list
    :return: list containing the original item
    """

    if not isinstance(item, list) and item is not None:
        return [item]

    else:
        return item


def decode_string(string):
    """
    Takes a string and removes BOM and decodes with correct codec

    :param string: the string to decode
    :return: decoded string
    """

    try:
        # string = string.replace('\xef\xbb\xbf', '')
        try:
            string = string.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            try:
                string = string.decode('latin-1').encode('utf-8')
            except UnicodeDecodeError:
                try:
                    string = str(string).decode('mac-roman').encode('utf-8')
                except UnicodeDecodeError:
                    sys.exit('Unable to parse this file as the encoding is not recognized.\n')
    except AttributeError:
        # str.decode() does not exist in Python 3, but str is always Unicode
        pass

    return string
