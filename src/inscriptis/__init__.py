
from lxml.html import fromstring

from inscriptis.html_engine import Inscriptis

__author__ = "Albert Weichselbraun, Fabian Odoni"
__copyright__ = "Copyright (C) 2016 Albert Weichselbraun, Fabian Odoni"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Fabian Odoni"
__email__ = "fabian.odoni@htwchur.ch"
__status__ = "Prototype"


def get_text(html_content):
    '''
    ::param: html_content
    ::returns:
        a text representation of the html content.
    '''
    html_tree = fromstring(html_content)
    parser = Inscriptis(html_tree)
    return parser.get_text()
