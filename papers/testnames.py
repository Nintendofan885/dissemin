# -*- encoding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#




import doctest
import unittest

import papers.name
from papers.name import match_names
from papers.name import name_similarity
from papers.name import name_unification
from papers.name import normalize_name_words
from papers.name import parse_comma_name
from papers.name import recapitalize_word
from papers.name import shallower_name_similarity
from papers.name import split_name_words
from papers.name import unify_name_lists


class MatchNamesTest(unittest.TestCase):

    def test_simple(self):
        self.assertTrue(match_names(('Robin', 'Ryder'), ('Robin', 'Ryder')))
        self.assertTrue(match_names(('Robin', 'Ryder'), ('R.', 'Ryder')))
        self.assertTrue(match_names(('R. J.', 'Ryder'), ('R.', 'Ryder')))
        self.assertFalse(match_names(('Jean', 'Dupont'), ('Joseph', 'Dupont')))
        self.assertFalse(match_names(('R. K.', 'Ryder'), ('J.', 'Ryder')))

    def test_reverse_order(self):
        self.assertTrue(match_names(('R. J.', 'Ryder'), ('J.', 'Ryder')))
        self.assertTrue(match_names(('W. T.', 'Gowers'), ('Timothy', 'Gowers')))

    def test_middle_initial(self):
        self.assertFalse(match_names(
            ('W. T. K.', 'Gowers'), ('Timothy', 'Gowers')))

    def test_hyphen(self):
        self.assertTrue(match_names(('J.-P.', 'Dupont'), ('J.', 'Dupont')))
        self.assertTrue(match_names(
            ('Jean-Pierre', 'Dupont'), ('J.-P.', 'Dupont')))

    def test_flattened_initials(self):
        self.assertFalse(match_names(
            ('Jamie Oliver', 'Ryder'), ('Jo', 'Ryder')))
        self.assertTrue(match_names(
            ('Jean-Pierre', 'Dupont'), ('JP.', 'Dupont')))
        self.assertTrue(match_names(
            ('Jean-Pierre', 'Dupont'), ('Jp.', 'Dupont')))

    def test_last_name(self):
        self.assertFalse(match_names(('Claire', 'Mathieu'),
                                     ('Claire', 'Kenyon-Mathieu')))

    def test_unicode(self):
        self.assertTrue(match_names(
            ('Thomas Émile', 'Bourgeat'), ('T. E.', 'Bourgeat')))


class SplitNameWordsTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(split_name_words('Jean'), (['Jean'], []))
        self.assertEqual(split_name_words('Jean Pierre'),
                         (['Jean', 'Pierre'], ['']))
        self.assertEqual(split_name_words('Jean-Pierre'),
                         (['Jean', 'Pierre'], ['-']))
        self.assertEqual(split_name_words('J.-P.'), (['J', 'P'], ['-']))
        self.assertEqual(split_name_words('J. P.'), (['J', 'P'], ['']))

    def test_awkward_spacing(self):
        self.assertEqual(split_name_words('J.P.'), (['J', 'P'], ['']))
        self.assertEqual(split_name_words('J.  P.'), (['J', 'P'], ['']))
        self.assertEqual(split_name_words('Jean - Pierre'),
                         (['Jean', 'Pierre'], ['-']))

    def test_unicode(self):
        self.assertEqual(split_name_words('Émilie'), (['Émilie'], []))
        self.assertEqual(split_name_words('José'), (['José'], []))
        self.assertEqual(split_name_words('José Alphonse'),
                         (['José', 'Alphonse'], ['']))
        self.assertEqual(split_name_words('É. R.'), (['É', 'R'], ['']))

    def test_flattened(self):
        self.assertEqual(split_name_words('JP.'), (['J', 'P'], ['-']))
        self.assertEqual(split_name_words('Jp.'), (['J', 'P'], ['-']))

    def test_abbreviation(self):
        self.assertEqual(split_name_words('Ms.'), (['Ms.'], []))
        self.assertEqual(split_name_words('St. Louis'),
                         (['St.', 'Louis'], ['']))

    def test_probably_not_flattened(self):
        self.assertEqual(split_name_words('Joseph.'), (['Joseph'], []))

    @unittest.expectedFailure
    def test_strange_characters(self):
        # TODO ?
        self.assertEqual(split_name_words('Jean*-Frederic'),
                         (['Jean', 'Frederic'], ['-']))


class NormalizeNameWordsTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(normalize_name_words('Jean'), 'Jean')
        self.assertEqual(normalize_name_words('Jean-Pierre'), 'Jean-Pierre')
        self.assertEqual(normalize_name_words('Jean-pierre'), 'Jean-Pierre')
        self.assertEqual(normalize_name_words('John Mark'), 'John Mark')
        self.assertEqual(normalize_name_words('JEAN-PIERRE'), 'Jean-Pierre')
        self.assertEqual(normalize_name_words('JOHN MARK'), 'John Mark')

    def test_unicode(self):
        self.assertEqual(normalize_name_words('JOSÉ'), 'José')
        self.assertEqual(normalize_name_words('JOSÉ-ALAIN'), 'José-Alain')
        self.assertEqual(normalize_name_words('José'), 'José')
        self.assertEqual(normalize_name_words('ÉMILIE'), 'Émilie')
        self.assertEqual(normalize_name_words('Émilie'), 'Émilie')

    def test_spacing(self):
        self.assertEqual(normalize_name_words('John  Mark'), 'John Mark')
        self.assertEqual(normalize_name_words(' John  Mark'), 'John Mark')
        self.assertEqual(normalize_name_words(' John Mark \n'), 'John Mark')
        self.assertEqual(normalize_name_words('Jean - Pierre'), 'Jean-Pierre')
        self.assertEqual(normalize_name_words('J.P.'), 'J. P.')

    def test_flattened(self):
        self.assertEqual(normalize_name_words('JP.'), 'J.-P.')
        self.assertEqual(normalize_name_words('Jp.'), 'J.-P.')

    def test_lower(self):
        self.assertEqual(normalize_name_words('catalin'), 'Catalin')
        self.assertEqual(normalize_name_words(
            'Colin de Verdière'), 'Colin de Verdière')

    def test_comma(self):
        self.assertEqual(normalize_name_words('John, Mark'), 'John Mark')
        self.assertEqual(normalize_name_words('John,, Mark'), 'John Mark')
        self.assertEqual(normalize_name_words('John Mark,'), 'John Mark')
        self.assertEqual(normalize_name_words('John Mark,,'), 'John Mark')
        self.assertEqual(normalize_name_words('John, Mark,,'), 'John Mark')

    def test_involutive(self):
        lst = [
                'Jean',
                'Jean-Pierre',
                'John Mark',
                'JEAN-PIERRE',
                'JOHN MARK',
                'JOSÉ',
                'JOSÉ-ALAIN',
                'José',
                'ÉMILIE',
                'Émilie',
                'John  Mark',
                'Jean - Pierre',
                'J.P. Morgan',
                'JP. Morgan',
                'Jp. Morgan',
              ]
        for sample in lst:
            normalized = normalize_name_words(sample)
            self.assertEqual(normalized, normalize_name_words(normalized))


class RecapitalizeWordTest(unittest.TestCase):

    def test_recapitalize_word(self):
        self.assertEqual(recapitalize_word('Dupont'), 'Dupont')
        self.assertEqual(recapitalize_word('van'), 'van')
        self.assertEqual(recapitalize_word('CLARK'), 'Clark')
        self.assertEqual(recapitalize_word(
            'GRANROTH-WILDING'), 'Granroth-Wilding')
        self.assertEqual(recapitalize_word('Jean-Pierre'), 'Jean-Pierre')

    def test_lower(self):
        self.assertEqual(recapitalize_word('van'), 'van')
        self.assertEqual(recapitalize_word('alphonse'), 'alphonse')

    def test_force(self):
        self.assertEqual(recapitalize_word('jean', True), 'Jean')

    def test_unicode(self):
        self.assertEqual(recapitalize_word('ÉMILIE'), 'Émilie')
        self.assertEqual(recapitalize_word('JOSÉ'), 'José')


class NameSimilarityTest(unittest.TestCase):

    def test_matching(self):
        self.assertAlmostEqual(
                name_similarity(('Robin', 'Ryder'), ('Robin', 'Ryder')), 0.8)
        self.assertAlmostEqual(
                name_similarity(('Robin', 'Ryder'), ('R.', 'Ryder')), 0.4)
        self.assertAlmostEqual(
                name_similarity(('R.', 'Ryder'), ('R.', 'Ryder')), 0.4)
        self.assertAlmostEqual(
                name_similarity(('Robin J.', 'Ryder'), ('R.', 'Ryder')), 0.3)
        self.assertAlmostEqual(
                name_similarity(('Robin J.', 'Ryder'), ('R. J.', 'Ryder')), 0.8)
        self.assertAlmostEqual(
                name_similarity(('R. J.', 'Ryder'), ('J.', 'Ryder')), 0.3)
        self.assertAlmostEqual(
                name_similarity(('Robin', 'Ryder'), ('Robin J.', 'Ryder')), 0.7)

    def test_multiple(self):
        self.assertAlmostEqual(
                name_similarity(('Juan Pablo', 'Corella'), ('J. Pablo', 'Corella')), 1.0)

    def test_reverse(self):
        self.assertAlmostEqual(
                name_similarity(('W. Timothy', 'Gowers'), ('Timothy', 'Gowers')), 0.7)

    def test_mismatch(self):
        self.assertAlmostEqual(
                name_similarity(('Robin K.', 'Ryder'), ('Robin J.', 'Ryder')), 0)
        self.assertAlmostEqual(
                name_similarity(('Claire', 'Mathieu'), ('Claire', 'Kenyon-Mathieu')), 0)
        self.assertAlmostEqual(
                name_similarity(('Amanda P.', 'Brown'), ('Patrick', 'Brown')), 0)

    def test_symmetric(self):
        pairs = [
            (('Robin', 'Ryder'), ('Robin', 'Ryder')),
            (('Robin', 'Ryder'), ('R.', 'Ryder')),
            (('R.', 'Ryder'), ('R.', 'Ryder')),
            (('Robin J.', 'Ryder'), ('R.', 'Ryder')),
            (('Robin J.', 'Ryder'), ('R. J.', 'Ryder')),
            (('R. J.', 'Ryder'), ('J.', 'Ryder')),
            (('Robin', 'Ryder'), ('Robin J.', 'Ryder')),
            (('W. Timothy', 'Gowers'), ('Timothy', 'Gowers')),
            (('Robin K.', 'Ryder'), ('Robin J.', 'Ryder')),
            (('Claire', 'Mathieu'), ('Claire', 'Kenyon-Mathieu')),
        ]
        for a, b in pairs:
            self.assertAlmostEqual(name_similarity(a, b), name_similarity(b, a))


class ShallowerNameSimilarityTest(unittest.TestCase):

    def test_matching(self):
        self.assertAlmostEqual(
            shallower_name_similarity(('Robin', 'Ryder'), ('Robin', 'Ryder')), 1.0)
        self.assertGreater(
            shallower_name_similarity(('Robin', 'Ryder'), ('R.', 'Ryder')), 0)
        self.assertGreater(
            shallower_name_similarity(('R.', 'Ryder'), ('R.', 'Ryder')), 0)
        self.assertGreater(
            shallower_name_similarity(('Robin J.', 'Ryder'), ('R.', 'Ryder')), 0)
        self.assertGreater(
            shallower_name_similarity(('Robin J.', 'Ryder'), ('R. J.', 'Ryder')), 0)
        self.assertGreater(
            shallower_name_similarity(('Robin', 'Ryder'), ('Robin J.', 'Ryder')), 0)
        self.assertGreater(
            shallower_name_similarity(('Robin', 'Ryder'), ('', 'Ryder')), 0)

    def test_multiple(self):
        self.assertAlmostEqual(
            shallower_name_similarity(('Juan Pablo', 'Corella'), ('J. Pablo', 'Corella')), 1.0)

    def test_unicode(self):
        self.assertGreater(
            shallower_name_similarity(('Cl\u0102\u0160ment', 'Pit-Claudel'), ('Clément', 'Pit-Claudel')), 0)

    def test_reverse(self):
        self.assertGreater(
                shallower_name_similarity(('W. Timothy', 'Gowers'), ('Timothy', 'Gowers')), 0)

    def test_mismatch(self):
        self.assertAlmostEqual(
                shallower_name_similarity(('Robin K.', 'Ryder'), ('Robin J.', 'Ryder')), 0)
        self.assertAlmostEqual(
                shallower_name_similarity(('Robin', 'Ryder'), ('Robin', 'Rider')), 0)

    def test_symmetric(self):
        pairs = [
            (('Robin', 'Ryder'), ('Robin', 'Ryder')),
            (('Robin', 'Ryder'), ('R.', 'Ryder')),
            (('R.', 'Ryder'), ('R.', 'Ryder')),
            (('Robin J.', 'Ryder'), ('R.', 'Ryder')),
            (('Robin J.', 'Ryder'), ('R. J.', 'Ryder')),
            (('R. J.', 'Ryder'), ('J.', 'Ryder')),
            (('Robin', 'Ryder'), ('Robin J.', 'Ryder')),
            (('W. Timothy', 'Gowers'), ('Timothy', 'Gowers')),
            (('Robin K.', 'Ryder'), ('Robin J.', 'Ryder')),
            (('Claire', 'Mathieu'), ('Claire', 'Kenyon-Mathieu')),
        ]
        for a, b in pairs:
            self.assertAlmostEqual(shallower_name_similarity(
                a, b), shallower_name_similarity(b, a))

    def test_malformed(self):
        inputs = [
            (('  ', '  '), ('John', 'Doe')),
            (('Alfred', 'Kastler'), ('    ', '    ')),
            ('', (None, '')),
            ]
        for a, b in inputs:
            self.assertEqual(shallower_name_similarity(a, b), False)

    def test_hyphen(self):
        self.assertGreater(
            shallower_name_similarity(('Clement F.', 'Pit Claudel'),
                                       ('Clément', 'Pit-Claudel')),
                                        0)

class ParseCommaNameTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(parse_comma_name(
            'Claire Mathieu'), ('Claire', 'Mathieu'))
        self.assertEqual(parse_comma_name(
            'Mathieu, Claire'), ('Claire', 'Mathieu'))
        self.assertEqual(parse_comma_name(
            'Kenyon-Mathieu, Claire'), ('Claire', 'Kenyon-Mathieu'))
        self.assertEqual(parse_comma_name('Arvind'), ('', 'Arvind'))

    def test_initial_capitalized(self):
        self.assertEqual(parse_comma_name(
            'MATHIEU Claire'), ('Claire', 'Mathieu'))
        self.assertEqual(parse_comma_name('MATHIEU C.'), ('C.', 'Mathieu'))

    def test_final_capitalized(self):
        self.assertEqual(parse_comma_name(
            'Claire MATHIEU'), ('Claire', 'Mathieu'))
        self.assertEqual(parse_comma_name('C. MATHIEU'), ('C.', 'Mathieu'))

    def test_initial_initials(self):
        self.assertEqual(parse_comma_name('C. Mathieu'), ('C.', 'Mathieu'))
        self.assertEqual(parse_comma_name('N. E. Young'), ('N. E.', 'Young'))

    def test_final_initials(self):
        self.assertEqual(parse_comma_name('Mathieu C.'), ('C.', 'Mathieu'))
        self.assertEqual(parse_comma_name('Gowers W. T..'), ('W. T.', 'Gowers'))

    def test_middle_initials(self):
        self.assertEqual(parse_comma_name(
            'Neal E. Young'), ('Neal E.', 'Young'))

    @unittest.expectedFailure
    def test_collapsed_initials(self):
        self.assertEqual(parse_comma_name('Badiou CS'), ('C. S.', 'Badiou'))
        self.assertEqual(parse_comma_name('Tony LI'), ('Tony', 'Li'))

    @unittest.expectedFailure
    def test_hard_cases(self):
        # TODO ?
        self.assertEqual(parse_comma_name('W. Timothy Gowers'),
                         ('W. Timothy', 'Gowers'))
        self.assertEqual(parse_comma_name('Guido van Rossum'),
                         ('Guido', 'van Rossum'))
        self.assertEqual(parse_comma_name(
            'Éric Colin de Verdière'), ('Éric', 'Colin de Verdière'))


class NameUnificationTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(name_unification(('Jean', 'Dupont'),
                                          ('Jean', 'Dupont')), ('Jean', 'Dupont'))
        self.assertEqual(name_unification(('J.', 'Dupont'),
                                          ('Jean', 'Dupont')), ('Jean', 'Dupont'))
        self.assertEqual(name_unification(('Anna', 'Erscher'),
                                          ('A. G.', 'Erscher')), ('Anna G.', 'Erscher'))

    def test_hyphens(self):
        self.assertEqual(name_unification(('J.-P.', 'Dupont'),
                                          ('Jean', 'Dupont')), ('Jean-P.', 'Dupont'))
        self.assertEqual(name_unification(('Jean Pierre', 'Dupont'), ('Jean', 'Dupont')),
                         ('Jean Pierre', 'Dupont'))
        self.assertEqual(name_unification(('Jean-Pierre', 'Dupont'), ('Jean', 'Dupont')),
                         ('Jean-Pierre', 'Dupont'))

        # For this one we don't check the output because ideally it
        # should be ('Clément F.', 'Pit-Claudel') but it is currently
        # ('Clement F.', 'Pit Claudel') which is still fine.
        self.assertTrue(name_unification(('Clement F.', 'Pit Claudel'),
                                            ('Clément', 'Pit-Claudel')))

    def test_uncommon_order(self):
        self.assertEqual(name_unification(('W. T.', 'Gowers'),
                                          ('Timothy', 'Gowers')), ('W. Timothy', 'Gowers'))

    def test_fix_capitalization(self):
        self.assertEqual(name_unification(('Marie-france', 'Sagot'),
                                          ('Marie-France', 'Sagot')), ('Marie-France', 'Sagot'))
        self.assertEqual(name_unification(('Marie-France', 'Sagot'),
                                          ('Marie-france', 'Sagot')), ('Marie-France', 'Sagot'))

    def test_flattened_initials(self):
        self.assertEqual(name_unification(('J. P.', 'Gendre'),
                                          ('Jp.', 'Gendre')), ('J.-P.', 'Gendre'))
        self.assertEqual(name_unification(('J. Pierre', 'Gendre'),
                                          ('Jp.', 'Gendre')), ('J.-Pierre', 'Gendre'))

    def test_empty_first_name(self):
        self.assertEqual(name_unification(
            ('', 'Placet'), ('Vincent', 'Placet')), ('Vincent', 'Placet'))

    def test_duplicated(self):
        # http://api.openaire.eu/oai_pmh?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:dnet:od_______567::b9714edf9d96bbe640f7a8d753be81b7
        self.assertEqual(name_unification(('A Adi', 'Shamir'),
                                          ('Adi', 'Shamir')), ('Adi', 'Shamir'))
        self.assertEqual(name_unification(('A A', 'Amarilli'),
                                          ('Antoine', 'Amarilli')), ('Antoine A.', 'Amarilli'))
        self.assertEqual(name_unification(('A A', 'Amarilli'),
                                          ('A', 'Amarilli')), ('A. A.', 'Amarilli'))
        self.assertEqual(name_unification(
            ('H-C Hsieh-Chung', 'Chen'), ('Hsieh-Chung', 'Chen')), ('Hsieh-Chung', 'Chen'))

    def test_quotes(self):
        self.assertNotEqual(name_unification(
            ('Alessandra', "D’Alessandro"),
            ('A.', "d'Alessandro")),
            None)

    @unittest.expectedFailure
    def test_composite_last_name(self):
        # TODO this should be reasonably easy to get right
        self.assertEqual(name_unification(('F.', 'Zappa Nardelli'),
                                          ('Francesco', 'Nardelli')), ('Francesco', 'Zappa Nardelli'))

    @unittest.expectedFailure
    def test_name_splitting_error(self):
        # TODO Not sure we can get that right with a reasonable rule
        self.assertEqual(name_unification(('Johannes G. de', 'Vries'), ('Johannes G.', 'de Vries')),
                         ('Johannes G.', 'de Vries'))
        self.assertEqual(name_unification(('Éric Colin', 'de Verdière'), ('E.', 'Colin de Verdière')),
                         ('Éric', 'Colin de Verdière'))


class UnifyNameListsTest(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(unify_name_lists([], []), [])
        self.assertEqual(unify_name_lists(
            [('Jean', 'Dupont')],
            [('Jean', 'Dupont')]),
            [(('Jean', 'Dupont'), (0, 0))])
        self.assertEqual(unify_name_lists(
            [('Jean', 'Dupont')],
            [('J.', 'Dupont')]),
            [(('Jean', 'Dupont'), (0, 0))])
        self.assertEqual(unify_name_lists(
            [('Jean', 'Dupont')],
            [('J. F.', 'Dupont')]),
            [(('Jean F.', 'Dupont'), (0, 0))])
        self.assertEqual(unify_name_lists(
            [('Jean', 'Dupont'), ('Marie', 'Dupré'), ('Alphonse', 'de Lamartine')],
            [('J.', 'Dupont'), ('M.', 'Dupré'), ('A.', 'de Lamartine')]),
            [(('Jean', 'Dupont'), (0, 0)), (('Marie', 'Dupré'), (1, 1)), (('Alphonse', 'de Lamartine'), (2, 2))])
        self.assertEqual(unify_name_lists(
            [('Antonin', 'Delpeuch'), ('Anne', 'Preller')],
            [('Antonin', 'Delpeuch'), ('Anne', 'Preller')]),
            [(('Antonin', 'Delpeuch'), (0, 0)), (('Anne', 'Preller'), (1, 1))])

    def test_insertion(self):
        self.assertEqual(unify_name_lists(
            [('Jean', 'Dupont'), ('Marie', 'Dupré'), ('Alphonse', 'de Lamartine')],
            [('J.', 'Dupont'), ('M.', 'Dupré'), ('A.', 'de Lamartine'), ('R.', 'Badinter')]),
            [(('Jean', 'Dupont'), (0, 0)), (('Marie', 'Dupré'), (1, 1)),
                (('Alphonse', 'de Lamartine'), (2, 2)), (('R.', 'Badinter'), (None, 3))])
        self.assertEqual(unify_name_lists(
            [('Élise', 'Chaumont'), ('Jean', 'Dupont'),
             ('Marie', 'Dupré'), ('Alphonse', 'de Lamartine')],
            [('J.', 'Dupont'), ('M.', 'Dupré'), ('A.', 'de Lamartine')]),
            [(('Élise', 'Chaumont'), (0, None)), (('Jean', 'Dupont'), (1, 0)), (('Marie', 'Dupré'), (2, 1)), (('Alphonse', 'de Lamartine'), (3, 2))])

    def test_same_last_name(self):
        self.assertTrue(unify_name_lists(
            [('Jean', 'Dupont'), ('Marie', 'Dupont')],
            [('M.', 'Dupont'), ('J. P.', 'Dupont')]) in
            [
                 [(('Jean P.', 'Dupont'), (0, 1)), (('Marie', 'Dupont'), (1, 0))],
                 [(('Marie', 'Dupont'), (1, 0)), (('Jean P.', 'Dupont'), (0, 1))]
            ])

    def test_dirty_input(self):
        self.assertEqual(unify_name_lists(
            [('Jérémie', 'Boutier'), ('Alphonse', 'Viger')],
            [('J{é}r{é}mie', 'Boutier'), ('A.', 'Viger')]),
            [(('Jérémie', 'Boutier'), (0, 0)), (('Alphonse', 'Viger'), (1, 1))])

    def test_duplicates(self):
        self.assertEqual(unify_name_lists(
            [('Jérémie', 'Boutier'), ('Jérémie', 'Boutier')],
            [('J.', 'Boutier')]),
            [(('Jérémie', 'Boutier'), (0, 0)), (None, (1, None))])

    def test_shallower_similarity(self):
        self.assertEqual(unify_name_lists(
            [('Clement F.', 'Pit Claudel')],
            [('Clément', 'Pit-Claudel')])[0][1],
            (0,0))

    def test_inverted(self):
        # in the wild:
        # https://doi.org/10.1371/journal.pone.0156198
        # http://hdl.handle.net/11573/870611
        self.assertEqual(len([x for x in unify_name_lists(
            [
                ('Sarnelli', 'Giovanni'),
                ("d'Alessandro", 'Alessandra'),
            ],
            [
                ('Giovanni', 'Sarnelli'),
                ('Giovanni', 'Domenico de Palma'),
                ('Alessandra', "D'Alessandro"),
            ]) if x[0] != None]),
            3)


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(papers.name))
    return tests
