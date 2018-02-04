#!/usr/bin/env python
# -*- coding: utf8 -*-

import unittest
from buzzword_poem_generator import (
    invert_map, find_poem_base, get_rhyme_words_from_syllables_num,
    get_rhyme_words_groups, fill_poem, is_rhyme, get_syllables_combinations, generate_poem,
)


class TestBuzzwordPoemGenerator(unittest.TestCase):
    """
    Test cases for Buzzword poem generator
    """

    def test_find_poem_base(self):
        """Test find_poem_base function"""
        words_syllables = {
            'One': 1,
            'Two': 1,
            'Three': 1,
            'Four': 1,
            'Five': 1,
            'Six': 1,
            'Eight': 1,
            'Nine': 1,
            'Ten': 1,
            'Seven': 2,
            'Eleven': 3,
            'Fourteen': 2,
            'Fifteen': 2,
            'Sixteen': 2,
            'Seventeen': 3,
        }
        syllables_words = invert_map(words_syllables)
        # only one combination for 3 syllables is provided, so only one poem base for [3, 3, 3] is possible
        poem_base = find_poem_base(syllables_words, {3: [(1, 1, 1,),]}, [3, 3, 3], min_words_in_line=1)
        self.assertEqual(poem_base, [(1, 1, 1), (1, 1, 1), (1, 1, 1)])
        # for combination {1: [(1,),]} and syllables_in_lines=[1, 1], the poem_base must be [(1,), (1,)]
        poem_base = find_poem_base(syllables_words, {1: [(1,),]}, [1, 1], min_words_in_line=1)
        self.assertNotEqual(poem_base, [(2,), (2,),])
        # for 2 syllables 2 combinations possible (1, 1) and (2), therefore use `assertIn`
        poem_base = find_poem_base(syllables_words, {
            1: [(1,),],
            2: [(1, 1,), (2,),],
        }, [1, 2], min_words_in_line=1)
        self.assertIn(poem_base, [
            [(1,), (1, 1)],
            [(1,), (2,)],
        ])
        poem_base = find_poem_base({}, {3: [(1, 1, 1,),]}, [3, 3, 3], min_words_in_line=1)
        self.assertEqual(poem_base, [])

        syllables_words = {
            1: ['One', 'Two',],
            2: ['Seven',],
        }
        poem_base = find_poem_base(syllables_words, {1: [(1,),], 2: [(2,),]}, [1, 2, 1], min_words_in_line=1)
        self.assertEqual(poem_base, [(1,), (2,), (1,)])
        # there are two words with two syllables in syllables_words, therefore result is [(1,), (1,),]
        poem_base = find_poem_base(syllables_words, {1: [(1,),], 2: [(2,),]}, [1, 1,], min_words_in_line=1)
        self.assertEqual(poem_base, [(1,), (1,),])
        # there is only one word with two syllables in syllables_words, therefore result is []
        poem_base = find_poem_base(syllables_words, {1: [(1,),], 2: [(2,),]}, [2, 2,], min_words_in_line=1)
        self.assertEqual(poem_base, [])

        # -1 min_words_in_line
        with self.assertRaises(Exception):
            find_poem_base(syllables_words, {1: [(1,),]}, [1,], min_words_in_line=-1)
        # 0 min_words_in_line
        with self.assertRaises(Exception):
            find_poem_base(syllables_words, {1: [(1,),]}, [1,], min_words_in_line=0)
        # min_words_in_line = 4 is more than 3 words maximum (3 * 1 syllable)
        with self.assertRaises(Exception):
            find_poem_base(syllables_words, {3: [(1, 1, 1,),]}, [3,], min_words_in_line=4)
        # no key 2 in {syllables: combinations} dict
        with self.assertRaises(Exception):
            find_poem_base(syllables_words, {1: [(1,),]}, [1, 2], min_words_in_line=1)

    def test_get_rhyme_words_from_syllables_num(self):
        """Test get_rhyme_words_from_syllables_num function"""
        words_syllables = {
            'Seven': 2,
            'Eleven': 3,
        }
        rhymes = [
            {'Seven', 'Eleven'},
        ]
        syllables_words = invert_map(words_syllables)

        # no rhymes for []
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [])
        self.assertEqual(rhyme_words, [])
        # no rhymes for [1,] syllable, because there are no words with 1 syllable
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [1])
        self.assertEqual(rhyme_words, [])
        # for [2] syllable, there is only ['Seven'] word, therefore rhyme
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [2])
        self.assertEqual(rhyme_words, ['Seven'])
        # no rhymes for [1, 2] syllables
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [1, 2])
        self.assertEqual(rhyme_words, [])
        # for [2, 3] there is ['Seven', 'Eleven'] rhyme
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [2, 3])
        self.assertEqual(rhyme_words, ['Seven', 'Eleven'])
        # for [3, 2] there is ['Eleven', 'Seven'] rhyme
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [3, 2])
        self.assertEqual(rhyme_words, ['Eleven', 'Seven'])

        words_syllables = {
            'Seven': 2,
            'Eleven': 3,
            'Fourteen': 2,
            'Fifteen': 2,
            'Sixteen': 2,
            'Seventeen': 3,
        }
        rhymes = [
            {'Seven', 'Eleven',},
            {'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen',},
        ]
        syllables_words = invert_map(words_syllables)
        # for [2, 2, 2] there is ['Fourteen', 'Sixteen', 'Fifteen'] rhyme
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [2, 2, 2])
        self.assertEqual(set(rhyme_words), set(['Fourteen', 'Sixteen', 'Fifteen']))
        # for [2, 2, 2, 3] there is ['Fourteen', 'Sixteen', 'Fifteen', 'Seventeen'] rhyme
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [2, 2, 2, 3])
        self.assertEqual(set(rhyme_words), set(['Fourteen', 'Sixteen', 'Fifteen', 'Seventeen']))
        # for [2, 2] there are several rhymes combinations, therefore use `assertIn`
        rhyme_words = get_rhyme_words_from_syllables_num(words_syllables, syllables_words, rhymes, [2, 2])
        self.assertIn(set(rhyme_words), [
            set(['Fourteen', 'Fifteen']), set(['Fourteen', 'Sixteen']), set(['Fifteen', 'Sixteen'])])

    def test_get_rhyme_words_groups(self):
        """Test get_rhyme_words_groups function"""
        words_syllables = {
            'Seven': 2,
            'Eleven': 3,
        }
        rhymes = [
            {'Seven', 'Eleven'},
        ]
        syllables_words = invert_map(words_syllables)

        # no rhyme words groups for empty syllables num groups
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[]])
        self.assertEqual(rhyme_words_groups, [])
        # no words with 1 syllable
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[1,]])
        self.assertEqual(rhyme_words_groups, [])
        # one word with 2 syllables
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2,]])
        self.assertEqual(rhyme_words_groups, [['Seven']])
        # no rhymes for [1, 2] syllables
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[1, 2]])
        self.assertEqual(rhyme_words_groups, [])
        # one rhyme for [2, 3] syllables
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2, 3]])
        self.assertEqual(rhyme_words_groups, [['Seven', 'Eleven']])

        words_syllables = {
            'One': 1,
            'Seven': 2,
            'Eleven': 3,
            'Fourteen': 2,
            'Seventeen': 3,
        }
        rhymes = [
            {'Seven', 'Eleven',},
            {'Fourteen', 'Seventeen',},
        ]
        syllables_words = invert_map(words_syllables)

        # sort rhyme words groups results, because they are returned in random order
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2, 3], [2, 3]])
        self.assertEqual(sorted(rhyme_words_groups), sorted([['Seven', 'Eleven'], ['Fourteen', 'Seventeen']]))
        # no rhyme words groups results, because all words have already been used
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2, 3], [2, 3], [2, 3]])
        self.assertEqual(sorted(rhyme_words_groups), [])
        # check empty rhyme group
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2, 3], [2, 3], []])
        self.assertEqual(sorted(rhyme_words_groups), sorted([['Seven', 'Eleven'], ['Fourteen', 'Seventeen']]))
        # check rhyme group with number of syllables = [1]
        rhyme_words_groups = get_rhyme_words_groups(words_syllables, syllables_words, rhymes, [[2, 3], [2, 3], [1]])
        self.assertEqual(sorted(rhyme_words_groups), sorted([['Seven', 'Eleven'], ['Fourteen', 'Seventeen'], ['One']]))

    def test_fill_poem(self):
        """Test fill_poem function"""
        words_syllables = {
            'One': 1,
            'Seven': 2,
            'Eleven': 3,
            'Fourteen': 2,
            'Seventeen': 3,
        }
        rhymes = [
            {'Seven', 'Eleven',},
            {'Fourteen', 'Seventeen',},
        ]
        syllables_words = invert_map(words_syllables)

        # sort the results, because poems are returned in random order
        poem = fill_poem(words_syllables, syllables_words, rhymes, [(2,), (3,), (2,), (3,)], 'AABB')
        self.assertEqual(sorted(poem), sorted([['Fourteen'], ['Seventeen'], ['Seven'], ['Eleven']]))
        # no poem, because there is no rhyme for syllables count [2, 2] and [3, 3]
        poem = fill_poem(words_syllables, syllables_words, rhymes, [(2,), (3,), (2,), (3,)], 'ABAB')
        self.assertEqual(poem, [])
        # no poem, because there is no rhyme for syllables count [3, 3]
        poem = fill_poem(words_syllables, syllables_words, rhymes, [(2,), (3,), (2,)], 'ABC')
        self.assertEqual(poem, [])
        # no poem, because there is no word with 0 syllables
        poem = fill_poem(words_syllables, syllables_words, rhymes, [(0,),], '0')
        self.assertEqual(poem, [])
        # no poem, for empty base abd rhyme scheme
        poem = fill_poem(words_syllables, syllables_words, rhymes, [], '')
        self.assertEqual(poem, [])

        words_syllables = {
            'One': 1,
            'Seven': 2,
            'Seventeen': 3,
            'Fifty': 2,
        }
        rhymes = []
        syllables_words = invert_map(words_syllables)

        # several poems can be generated
        poem = fill_poem(words_syllables, syllables_words, rhymes, [(1, 3,), (2, 2),], 'AB')
        self.assertIn(poem, (
            [['One', 'Seventeen'], ['Seven', 'Fifty']],
            [['One', 'Seventeen'], ['Fifty', 'Seven']],
            [['Seven', 'Fifty'], ['One', 'Seventeen']],
            [['Fifty', 'Seven'], ['One', 'Seventeen']],
        ))

        # The number of lines (2) != rhyme scheme size (3)
        with self.assertRaises(Exception):
            fill_poem(words_syllables, syllables_words, rhymes, [(1, 2), (2, 3)], 'ABC')
        with self.assertRaises(Exception):
            fill_poem(words_syllables, syllables_words, rhymes, [(1, 2), (2, 3), (2, 1)], 'AA')

    def test_get_syllables_combinations(self):
        """Test get_syllables_combinations function"""
        words_syllables = {
            'One': 1,
            'Seven': 2,
            'Eleven': 3,
            'Fourteen': 2,
        }
        syllables_words = invert_map(words_syllables)

        # no combinations for number of syllables = 0
        combinations = get_syllables_combinations(syllables_words, 0, use_cache=False)
        self.assertEqual(combinations, [[]])
        # one combination for number of syllables = 1
        combinations = get_syllables_combinations(syllables_words, 1, use_cache=False)
        self.assertEqual(combinations, [[1]])
        # one combination for number of syllables = 2
        combinations = get_syllables_combinations(syllables_words, 2, use_cache=False)
        self.assertEqual(sorted(combinations), sorted([[1, 1], [2]]))
        # one combination for number of syllables = 3
        combinations = get_syllables_combinations(syllables_words, 3, use_cache=False)
        self.assertEqual(sorted(combinations), sorted([[1, 1, 1], [1, 2], [2, 1], [3]]))

        # one combination for number of syllables = 1, use_cache=True
        combinations = get_syllables_combinations(syllables_words, 1, use_cache=True)
        self.assertEqual(combinations, [[1]])
        # one combination for number of syllables = 1, use_cache=True again to check load from cache
        combinations = get_syllables_combinations(syllables_words, 1, use_cache=True)
        self.assertEqual(combinations, [[1]])

    def test_generate_poem(self):
        """Test generate_poem function"""
        generate_poem('A', [1], 1, False)
        # poem can't be generated error
        generate_poem('ABCDE', [4, 4, 4, 4, 4], 4, False)
        # must print errors
        generate_poem('A', [1], 0, False)
        generate_poem('A', [1], 3, False)
        generate_poem('ABC', [1], 0, False)
        generate_poem('A', [99999], 0, False)

    def test_is_rhyme(self):
        """Test is_rhyme function"""
        rhymes = [
            {'Seven', 'Eleven',},
            {'Thirteen', 'Fourteen', 'Seventeen',},
        ]
        self.assertFalse(is_rhyme([''], rhymes))
        self.assertTrue(is_rhyme(['Seven'], rhymes))
        self.assertTrue(is_rhyme(['Seven', 'Eleven'], rhymes))
        self.assertTrue(is_rhyme(['Thirteen', 'Fourteen', 'Seventeen'], rhymes))
        self.assertTrue(is_rhyme(['Seventeen', 'Fourteen', 'Thirteen'], rhymes))
        self.assertFalse(is_rhyme(['Seventeen', 'Fourteen', 'Seven'], rhymes))

    def test_invert_map(self):
        """Test invert_map function"""
        self.assertEqual(invert_map({}), {})
        self.assertEqual(invert_map(invert_map({})), {})
        self.assertNotEqual(invert_map({}), {'a': 'b'})
        self.assertEqual(invert_map({'a': 123}), {123: ['a']})
        self.assertEqual(sorted(invert_map({'a': 1, 'b': 1, 'c': 2})[1]), sorted(['a', 'b']))


if __name__ == '__main__':
    unittest.main(verbosity=1)
