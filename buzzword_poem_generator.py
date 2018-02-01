#!/usr/bin/env python
# coding: utf-8

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
    'Tensorflow': 3,

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
    'Couchbase': 3,
    'Redshift': 2,
    'Postgres': 2,
    'Memcached': 2,
    'Cassandra': 3,
    'Redshift': 2,
    'Riak': 2,
    'HBase': 2,
}

RHYMES = [
    {'Rust', 'Raft', 'React',},
    {'Spark', 'Erlang',},
    {'Go', 'Tensorflow', 'Mongo',},
    {'Terraform', 'Storm', 'Swarm',},
    {'Scala', 'Impala',},
    {'Postgres', 'HBase', 'Couchbase',},
    {'Redis', 'Travis', 'Kinesis',},
    {'Hadoop', 'Sqoop',},
    {'RabbitMQ', 'ActiveMQ',},
    {'Celery', 'Sentry',},
]

# build map of {syllables: buzzwords with syllables}
SYLLABLES_WORDS = {}
for k, v in WORDS_SYLLABLES.items():
    SYLLABLES_WORDS[v] = SYLLABLES_WORDS.get(v, []) + [k]

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
            # currently used words for syllable {syllables: words count}, i.e. [2, 3, 2] -> {2: 2, 3: 1}
            cur_used = {x: combination.count(x) for x in set(combination)}
            # check if current combination is suitable
            suitable = True
            for syllables, words_count in cur_used.items():
                # if words count in current combination more than left available - find next combination
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
    if not used_rhyme_words:
        used_rhyme_words = []
    syllables_num_count = {}
    for n in syllables_num:
        syllables_num_count[n] = syllables_num_count.get(n, 0) + 1
    # remove already used rhyme words from rhymes
    unique_rhymes = [list(r) for r in RHYMES]
    for rhyme in unique_rhymes:
        for used_rhyme_word in used_rhyme_words:
            if used_rhyme_word in rhyme:
                rhyme.remove(used_rhyme_word)
    # find the rhymes for the list of syllables count
    found_rhymes = []
    for rhyme in unique_rhymes:
        rhyme_syllables = [WORDS_SYLLABLES[r] for r in rhyme]
        # build a map of {number of syllables: list of rhymes}
        nd = {}
        for num in syllables_num:
            for rs_num, rh in zip(rhyme_syllables, rhyme):
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


def get_rhyme_words_groups_from_syllables_num_groups(syllables_num_groups):
    """
    Get the groups of rhyme words from the groups of the syllables count lists
    E.g. for groups = [1, 2], [1, 3] returns ['Sqoop', 'Hadoop'], ['Go', 'Tensorflow']
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


def fill_poem(found_lines, rhyme_scheme):
    """Fill the poem with the words"""
    if len(found_lines) != len(rhyme_scheme):
        raise Exception('The number of lines != rhyme scheme!')

    # group last words in found lines by rhyme scheme
    sheme_last_word = {}
    for k, v in zip(rhyme_scheme, [x[-1] for x in found_lines]):
        sheme_last_word[k] = sheme_last_word.get(k, []) + [v]

    rhyme_words_groups = get_rhyme_words_groups_from_syllables_num_groups(sheme_last_word.values())
    if not rhyme_words_groups:
        return []

    rhyme_scheme_letter_last_words = dict(zip(sheme_last_word.keys(), rhyme_words_groups))
    current_SYLLABLES_WORDS = copy.deepcopy(SYLLABLES_WORDS)
    # flatten values lists
    last_words_values = sum(rhyme_scheme_letter_last_words.values(), [])
    # remove last words
    for last_word in last_words_values:
        current_SYLLABLES_WORDS[WORDS_SYLLABLES[last_word]].remove(last_word)

    # fill the poem with words
    poem = []
    for rhyme_scheme_letter, found_line in zip(rhyme_scheme, found_lines):
        last_word = rhyme_scheme_letter_last_words[rhyme_scheme_letter].pop(0)
        line = [current_SYLLABLES_WORDS[x].pop(0) for x in found_line[:-1]] + [last_word]
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
                    combinations.append(filter(None, v))
        if use_cache:
            with open('compositions_{}_{}.dat'.format(KEYS_HASH, syllables_num), 'wb') as f:
                f.write(pickle.dumps(combinations))
    return combinations


def main():
    """Main"""

    rhyme_scheme = 'ABAB'
    syllables_in_lines = [7, 7, 7, 6]
    min_words_in_line = 3
    combinations = {syllables: get_syllables_combinations(syllables) for syllables in syllables_in_lines}

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


if __name__ == '__main__':
    main()
