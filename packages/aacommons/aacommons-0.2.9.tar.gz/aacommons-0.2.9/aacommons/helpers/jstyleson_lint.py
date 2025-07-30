#!/bin/env python3
#
# Copyright 2023 Thomas Bastian, Jeffrey Goff, Albert Pang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

'''
#
# Basic linting tool for jstyleson compatible JSON files
#
# Normally a jstyleson JSON file that has a typo in it will
# throw an error from the standard JSON library, but the
# line number reported in the exception will not match
# the original jstyleson JSON file line number
#
# This script will provide a contextual blob around 
# the bad line so the caller may search the original
# JSON file for a string rather than a line number
#
# Authors: Jeffrey Goff
#
'''
'''
# Usage Notes
# -----------
# The script can only find one error at a time, thus fix any
# error that is found, then re-run the script to check for
# further errors
#
'''
import json
import jstyleson
import os
import re
import sys

def usage_exit(msg=None):
    if msg:
        print(msg + "\n")
    print(f"usage: {sys.argv[0]} <path to arcli.json> [#lines]")
    print()
    print("#lines: # of lines to show around the error, min: 2, max: 20, default: 5")
    print()
    sys.exit()

if len(sys.argv) < 2:
    usage_exit()

ar = sys.argv[1]
if not os.path.exists(ar):
    usage_exit(f"warning: cannot find input file at: {ar}")

# plus/minus number of lines to show around the error
err_width = 5

if len(sys.argv) > 2:
    try:
        err_width = int(sys.argv[2])
        if err_width < 2 or err_width > 20:
            raise ValueError
    except ValueError:
        usage_exit("invalid value for #lines, must be an integer between 2 and 20")

# strip comments
cleaned_json = jstyleson.dispose(open(ar).read())

# remove any trailing newline to avoid offset error
cleaned_json = cleaned_json.lstrip()

# line buffer
buf = cleaned_json.split("\n")
print(f"Loaded {len(buf)} lines of cleaned json\n")

# catch exceptions from the regulation json package
try:
    json.loads(cleaned_json)
    print("Done, no errors found")
except json.decoder.JSONDecodeError as e:
    print(f"JSONDecodeError: {e}\n")
    m = re.match("(.*)?: line (\\d+) column (\\d+) \(char \\d+\)", str(e))
    if m:
        err_line = int(m.groups()[1])
        print(f"Displaying +/- {err_width} lines around the error line {err_line}\n")
        for i, l in enumerate(buf[err_line-err_width:err_line+err_width]):
            print(f"{i+err_line-err_width:<5} | {l}")
        print()
    print("Fix the error and then re-run the linter script")

print()

