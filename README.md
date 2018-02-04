# Buzzword poem generator

[![Build Status](https://travis-ci.org/delimitry/buzzword_poem_generator.svg?branch=master)](https://travis-ci.org/delimitry/buzzword_poem_generator)
[![Coverage Status](https://coveralls.io/repos/github/delimitry/buzzword_poem_generator/badge.svg?branch=master)](https://coveralls.io/github/delimitry/buzzword_poem_generator?branch=master)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/delimitry/buzzword_poem_generator/blob/master/LICENSE)

Description:
------------

Buzzword poem generator is a tool in pure Python for generation of the poems from the buzzwords.

This project was inspired by this twit: https://twitter.com/lenadroid/status/957054198872293378

Usage:
------
The usage of `buzzword_poem_generator.py` is simple:
```
usage: buzzword_poem_generator.py [-h] -r RHYME_SCHEME -s SYLLABLES_IN_LINES
                                  [SYLLABLES_IN_LINES ...]
                                  [-m MIN_WORDS_IN_LINE] [-c CACHE]

Buzzword poem generator

required arguments:
  -r RHYME_SCHEME       rhyme scheme (e.g.: ABAB, AABB)
  -s SYLLABLES_IN_LINES [SYLLABLES_IN_LINES ...]
                        syllables in lines (e.g.: 7 6 7 6)

optional arguments:
  -h, --help            show this help message and exit
  -m MIN_WORDS_IN_LINE  minimum number of words in line (1 by default)
  -c CACHE              use cache (True by default)
```

### Examples:

Four line buzzword poems with ABAB rhyme scheme and seven syllables per line:

`python buzzword_poem_generator.py -r ABAB -s 7 7 7 7 -m 3`

```
Kinesis Flink Hadoop Swarm
Impala Splunk Riak Raft
Couchbase Go HBase Storm
Zookeeper Sqoop Nomad Rust
```

`python buzzword_poem_generator.py -r ABAB -s 7 7 7 7`

```
Hadoop Riak HBase Raft
Nomad Logstash Kotlin Go
Docker Lambda Mongo Rust
Redshift Swarm TensorFlow
```

Five line buzzword poem with ABABA rhyme scheme and seven syllables per line:

`python buzzword_poem_generator.py -r ABABA -s 7 7 7 7 7`

```
Splunk Swarm Hazelcast Flink Rust
Chef Hive Couchbase Vault Sqoop
Storm Go Cassandra Spark Raft
Lambda Terraform Hadoop
Erlang Celery React
```

License:
--------
Released under [The MIT License](https://github.com/delimitry/buzzword_poem_generator/blob/master/LICENSE).
