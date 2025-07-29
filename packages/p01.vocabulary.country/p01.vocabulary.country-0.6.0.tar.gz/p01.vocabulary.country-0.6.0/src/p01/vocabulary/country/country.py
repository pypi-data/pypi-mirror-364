##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id: country.py 39 2007-01-28 07:08:55Z roger.ineichen $
"""

from __future__ import absolute_import

import os
import os.path

import six
import zope.interface
from p01.util import ucsv
from p01.vocabulary.country.i18n import MessageFactory as _
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


def to_unicode(value):
    if isinstance(value, six.binary_type):
        return six.text_type(value, 'utf-8')
    return six.text_type(value)


def csvVocabulary(fName):
    filename = os.path.join(os.path.dirname(__file__), 'data', fName)

    # Open the file in right mode
    mode = 'rb' if six.PY2 else 'r'
    with open(filename, mode) as f:
        reader = ucsv.UnicodeReader(f, delimiter=";")

        terms = []
        for id, title in reader:
            id = to_unicode(id)
            title = to_unicode(title)
            msg = _(title, default=title)
            terms.append(SimpleTerm(id, title=msg))

    return SimpleVocabulary(terms)

try:
    iso3166Alpha2CountryVocabularyData = csvVocabulary('iso-3166-alpha-2.csv')

    @zope.interface.implementer(IVocabularyFactory)
    def ISO3166Alpha2CountryVocabulary(context):
        return iso3166Alpha2CountryVocabularyData
except IOError:
    # data not generated
    iso3166Alpha2CountryVocabularyData = None
    ISO3166Alpha2CountryVocabulary = None


try:
    iso3166Alpha3CountryVocabularyData = csvVocabulary('iso-3166-alpha-3.csv')

    @zope.interface.implementer(IVocabularyFactory)
    def ISO3166Alpha3CountryVocabulary(context):
        return iso3166Alpha3CountryVocabularyData
except IOError:
    # data not generated
    iso3166Alpha3CountryVocabularyData = None
    ISO3166Alpha3CountryVocabulary = None


try:
    from p01.vocabulary.country.mapping import alpha2to3
    from p01.vocabulary.country.mapping import alpha3to2
except ImportError:
    # data not generated
    alpha2to3 = None
    alpha3to2 = None
