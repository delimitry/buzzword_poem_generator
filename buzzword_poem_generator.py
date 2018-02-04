#!/usr/bin/env python
# coding: utf-8
"""
Buzzword poem generator - a tool for generating the poems from the buzzwords.
"""

from __future__ import print_function

import argparse
import copy
import itertools
import os
import pickle
import random


MAX_TRIES = 100

WORDS_SYLLABLES = {
    'Go': 1,
    'Rust': 1,
    'Python': 2,
    'Haskell': 2,
    'Erlang': 2,
    'Kotlin': 2,
    'Scala': 2,

    'Raft': 1,
    'Paxos': 2,

    'React': 2,
    'TensorFlow': 3,
    'Keras': 2,

    'Swarm': 1,
    'Kubernetes': 4,
    'Mesos': 2,

    'Docker': 2,
    'Vagrant': 2,
    'Hadoop': 2,
    'Zookeeper': 3,
    'Terraform': 3,
    'Vault': 1,
    'Consul': 2,
    'Nomad': 2,

    'Ansible': 3,
    'Puppet': 2,
    'Chef': 1,

    'Hive': 1,
    'Spark': 1,
    'Impala': 3,
    'Flink': 1,
    'Storm': 1,
    'Celery': 3,
    'Lambda': 2,

    'Jenkins': 2,
    'Travis': 2,

    'Splunk': 1,
    'Sentry': 2,

    'Kafka': 2,
    'Kinesis': 3,
    'Logstash': 2,
    'RabbitMQ': 4,
    'Sqoop': 1,
    'ActiveMQ': 4,

    'Hazelcast': 3,
    'Mongo': 2,
    'Redis': 2,
    'Couchbase': 2,
    'Postgres': 2,
    'Memcached': 2,
    'Cassandra': 3,
    'Redshift': 2,
    'Riak': 2,
    'HBase': 2,
}

RHYMES = [
    {'Rust', 'Raft', 'React',},
    {'Spark', 'Erlang', 'Splunk',},
    {'Go', 'TensorFlow', 'Mongo',},
    {'Terraform', 'Storm', 'Swarm',},
    {'Scala', 'Impala',},
    {'Postgres', 'HBase', 'Couchbase',},
    {'Redis', 'Travis', 'Kinesis',},
    {'Hadoop', 'Sqoop',},
    {'RabbitMQ', 'ActiveMQ',},
    {'Celery', 'Sentry',},
]

WORDS_WITH_RHYME = set(sum([list(rl) for rl in RHYMES], []))


def invert_map(map_val):
    """Invert map, i.e. from {'a': 1, 'b': 1} get {1: ['a', 'b']}"""
    inv_map = {}
    for k, v in map_val.items():
        inv_map[v] = inv_map.get(v, []) + [k]
    return inv_map


# build map of {syllables: buzzwords with syllables}
SYLLABLES_WORDS = invert_map(WORDS_SYLLABLES)

SYLLABLES_KEYS = sorted([0] + list(SYLLABLES_WORDS.keys()))
KEYS_HASH = hash(tuple(SYLLABLES_KEYS)) & 0xffffffff


def find_poem_base(combinations, syllables_in_lines, min_words_in_line=3):
    """Find poem base with required number of syllables in lines"""
    if min_words_in_line > max(syllables_in_lines):
        raise Exception('Min words in line is more than max number of syllables in lines!')

    for syllables in combinations:
        random.shuffle(combinations[syllables])
    # total available words for syllable {syllables: words count}
    total_available = {x: len(SYLLABLES_WORDS[x]) for x in SYLLABLES_WORDS}
    found_lines = []

    # find a combination for each required number of syllables in line
    for syllables_in_line in syllables_in_lines:
        for combination in combinations[syllables_in_line]:
            if len(combination) < min_words_in_line:
                continue
            # make map {syllables: words count}, i.e. [2, 3, 2] -> {2: 2, 3: 1}
            cur_used = {x: combination.count(x) for x in set(combination)}
            # check if current combination is suitable
            suitable = True
            for syllables, words_count in cur_used.items():
                # find next combination if words count in current one is more than left available
                if words_count > total_available[syllables]:
                    suitable = False
            if not suitable:
                continue
            # for suitable combination - reduce the number of available syllables
            for syllables, words_count in cur_used.items():
                total_available[syllables] -= words_count
            found_lines.append(combination)
            break
        # stop if found all the lines
        if len(found_lines) >= len(syllables_in_lines):
            break
    # return empty lines if not found all required lines
    if len(found_lines) < len(syllables_in_lines):
        return []
    return found_lines


def get_rhyme_words_from_syllables_num(syllables_num, used_rhyme_words=None):
    """
    Get rhyme words from the list of syllables count
    E.g. for syllables_num [1, 2] returns ['Sqoop', 'Hadoop']
    Use argument used_rhyme_words to set already used words
    """
    if not syllables_num:
        return []
    if not used_rhyme_words:
        used_rhyme_words = []

    # if length of syllables_num is 1, return random word that has no rhyme
    if len(syllables_num) == 1:
        if used_rhyme_words:
            available_words = copy.deepcopy(WORDS_SYLLABLES)
            # remove all rhymes for used rhyme words from available words
            for used_rhyme_word in used_rhyme_words:
                for rhyme_line in RHYMES:
                    if used_rhyme_word in rhyme_line:
                        for rhyme_word in rhyme_line:
                            if rhyme_word in available_words:
                                available_words.pop(rhyme_word)
                # if used word has no rhymes - remove it
                if used_rhyme_word in available_words:
                    available_words.pop(used_rhyme_word)
            available_syllables_words = invert_map(available_words)
        else:
            # if used_rhyme_words is empty just get the random word with syllables_num
            available_syllables_words = SYLLABLES_WORDS
        return [random.choice(available_syllables_words[syllables_num[0]])]

    syllables_num_count = {}
    for n in syllables_num:
        syllables_num_count[n] = syllables_num_count.get(n, 0) + 1
    # remove already used rhyme words from rhymes
    unique_rhymes = [list(r) for r in RHYMES]
    for rhyme_line in unique_rhymes:
        for used_rhyme_word in used_rhyme_words:
            if used_rhyme_word in rhyme_line:
                rhyme_line.remove(used_rhyme_word)
    # find the rhymes for the list of syllables count
    found_rhymes = []
    for rhyme_line in unique_rhymes:
        rhyme_syllables = [WORDS_SYLLABLES[r] for r in rhyme_line]
        # build a map of {number of syllables: list of rhymes}
        nd = {}
        for num in syllables_num:
            for rs_num, rh in zip(rhyme_syllables, rhyme_line):
                if num == rs_num:
                    nd[num] = list(set(nd.get(num, []) + [rh]))
        # if found all syllables_num - add to found list
        syllables_count = {k: len(v) for k, v in nd.items()}
        if syllables_count == syllables_num_count:
            found_rhymes.append(nd)
    if not found_rhymes:
        return []
    # pick random rhyme from found list
    found_rhyme = random.choice(found_rhymes)
    # pop first word  with `syllables_num` from `found_rhyme` list
    result = [found_rhyme[n].pop(0) for n in syllables_num]
    return result


def get_rhyme_words_groups(syllables_num_groups):
    """
    Get the groups of rhyme words from the groups of the syllables count lists
    E.g. for groups = [1, 2], [1, 3] returns ['Sqoop', 'Hadoop'], ['Go', 'TensorFlow']
    """
    result = []
    used_rhyme_words = set()
    for group in syllables_num_groups:
        rhyme_words = get_rhyme_words_from_syllables_num(group, used_rhyme_words=used_rhyme_words)
        if not rhyme_words:
            return []
        used_rhyme_words |= set(rhyme_words)
        result.append(rhyme_words)
    return result


def fill_poem(found_base_lines, rhyme_scheme):
    """Fill the poem with the words, as the poem base consists of the number of syllables"""
    if len(found_base_lines) != len(rhyme_scheme):
        raise Exception('The number of lines != rhyme scheme!')

    # group last words in found lines by rhyme scheme letters
    # for example from [('A', 1), ('B', 1), ('A', 1), ('B', 3)] to {'A': [1, 1], 'B': [1, 3]}
    sheme_last_word = {}
    for k, v in zip(rhyme_scheme, [x[-1] for x in found_base_lines]):
        sheme_last_word[k] = sheme_last_word.get(k, []) + [v]

    # get the groups of rhyme words from the groups of syllables num
    rhyme_words_groups = get_rhyme_words_groups(sheme_last_word.values())
    if not rhyme_words_groups:
        return []

    rhyme_scheme_letter_last_words = dict(zip(sheme_last_word.keys(), rhyme_words_groups))
    current_syllables_words = copy.deepcopy(SYLLABLES_WORDS)
    # flatten values lists
    last_words_values = sum(rhyme_scheme_letter_last_words.values(), [])
    # remove last words
    for last_word in last_words_values:
        current_syllables_words[WORDS_SYLLABLES[last_word]].remove(last_word)

    # fill the poem with words
    poem = []
    for rhyme_scheme_letter, found_line in zip(rhyme_scheme, found_base_lines):
        last_word = rhyme_scheme_letter_last_words[rhyme_scheme_letter].pop(0)
        line = [current_syllables_words[x].pop(0) for x in found_line[:-1]] + [last_word]
        poem.append(line)
    return poem


def is_rhyme(words, rhymes):
    """Check the words are rhyme"""
    for r in rhymes:
        if all([w in r for w in words]):
            return True
    return False


def get_syllables_combinations(syllables_num, use_cache=True):
    """
    Get all possible compositions of `syllables_num`, i.e. all combinations,
    where a sum of positive integers is equal to `syllables_num`
    """
    combinations = []
    # if already computed and cache is used - load combinations from file
    fn = 'compositions_{}_{}.dat'.format(KEYS_HASH, syllables_num)
    if os.path.isfile(fn) and use_cache:
        with open(fn, 'rb') as f:
            combinations = pickle.load(f)
    else:
        for v in itertools.product(SYLLABLES_KEYS, repeat=syllables_num):
            if sum(v) == syllables_num:
                if v not in combinations:
                    combinations.append([x for x in v if x])
        if use_cache:
            with open('compositions_{}_{}.dat'.format(KEYS_HASH, syllables_num), 'wb') as f:
                f.write(pickle.dumps(combinations))
    return combinations


def main():
    """Main"""
    # prepare argument parser
    parser = argparse.ArgumentParser(description='Buzzword poem generator')
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-r', dest='rhyme_scheme', type=str,
        help='rhyme scheme (e.g.: ABAB, AABB)', required=True)
    required.add_argument(
        '-s', dest='syllables_in_lines', type=int, nargs='+',
        help='syllables in lines (e.g.: 7 6 7 6)', required=True)
    parser.add_argument(
        '-m', dest='min_words_in_line', type=int,
        help='minimum number of words in line (1 by default)', default=1, required=False)
    parser.add_argument(
        '-c', dest='cache', type=str,
        help='use cache (True by default)', default='1', required=False)
    parser._action_groups.append(optional)

    args = parser.parse_args()
    if not (args.rhyme_scheme and args.syllables_in_lines):
        parser.print_help()
        return

    rhyme_scheme = args.rhyme_scheme
    syllables_in_lines = args.syllables_in_lines
    min_words_in_line = args.min_words_in_line
    use_cache = args.cache.lower() in ['1', 'true', 't', 'on']

    try:
        if len(rhyme_scheme) != len(syllables_in_lines):
            raise Exception('The rhyme scheme size is not equal to number of syllables in lines!')
        if sum(syllables_in_lines) > sum(WORDS_SYLLABLES.values()):
            raise Exception('The sum of syllables in lines is more than sum of all syllables in available words!')

        combinations = {syls: get_syllables_combinations(syls, use_cache) for syls in syllables_in_lines}

        # try to find poem in MAX_TRIES tries
        try_number = 0
        while True:
            if try_number > MAX_TRIES:
                print("A poem can't be generated :(")
                break
            poem_base = find_poem_base(combinations, syllables_in_lines, min_words_in_line=min_words_in_line)
            if poem_base:
                poem = fill_poem(poem_base, rhyme_scheme)
                if poem:
                    print('\n'.join([' '.join(line) for line in poem]))
                    break
            try_number += 1
            continue
    except Exception as ex:
        print('Error: {}'.format(ex))


if __name__ == '__main__':
    main()
