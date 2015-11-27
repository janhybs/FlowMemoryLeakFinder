#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import os, sys, re


def alloc(items, filepath, line_number, regex_result):
    rel_filepath = filepath[str(filepath).index('src') + 4:]
    key = rel_filepath + ':' + regex_result[0][1]
    if key not in items:
        items[key] = { }
    if 'alloc' in items[key]:
        # print 'collision', items[key], line_number
        pass
    items[key].update({ 'loc': filepath, 'alloc': regex_result, 'aln': line_number })


def dealloc(items, filepath, line_number, regex_result):
    rel_filepath = filepath[str(filepath).index('src') + 4:]
    key = rel_filepath + ':' + regex_result[0][1]
    if key not in items:
        items[key] = { }
    if 'dealloc' in items[key]:
        # print 'collision ', items[key], line_number
        pass
    items[key].update({ 'loc': filepath, 'dealloc': regex_result, 'dln': line_number })


def process_file(f):
    allocations = { }
    with open(f, 'r') as fp:
        ln = 0
        lines = fp.readlines()
        for line in lines:
            ln += 1
            if line.strip().startswith('//') or line.strip().startswith('*'):
                continue

            new_result = new_alloc_regex.findall(line)
            if new_result:
                alloc(allocations, f, ln, new_result)

            delete_result = delete_alloc_regex.findall(line)
            if delete_result:
                dealloc(allocations, f, ln, delete_result)

    for name, item in allocations.items():
        if 'alloc' in item and 'dealloc' in item:
            del allocations[name]

    if allocations:
        # print f
        for name, item in allocations.items():
            if 'alloc' in item and 'dealloc' in item:
                print 'correct           {name:60s}:{aln:4d} - {dln:4d}'.format(name=name, **item)

            if 'alloc' in item and 'dealloc' not in item:
                print 'allocation-only   {name:60s}:{aln:4d} -  ???: {line}'.format(name=name, line=lines[item['aln']-1].strip(), **item)

            if 'alloc' not in item and 'dealloc' in item:
                print 'deallocation-only {name:60s}: ??? - {dln:4d}: {line}'.format(name=name, line=lines[item['dln']-1].strip(), **item)

        # print ''


location = sys.argv[1]# + '/coupling'

new_alloc_regex = re.compile(
    r'(([a-zA-Z0-9_]+)\s*=\s*new[^a-zA-Z_])'
)
delete_alloc_regex = re.compile(
    r'(delete\s*\[?\]?\s+([a-zA-Z0-9_]+))'
)
all_files = list()
for root, dirs, files in os.walk(location):
    if '/dealii' in root:
        continue
    for f in files:
        if f.split('.')[-1] in ('cc', 'hh', 'c', 'h', 'cpp', 'hpp'):
            all_files.append(os.path.join(root, f))

all_files = sorted(all_files)
for f in all_files:
    process_file(f)
