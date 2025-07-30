#
# Copyright 2021 Thomas Bastian, Jeffrey Goff, Albert Pang
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
# ARCLI sample runner.
#
# Authors: Thomas Bastian, Jeff Goff
#
'''

'''
# Parameters
'''
'''
#
'''

import argparse
import logging.config
import json
import os
#import pandas as pd
import sys
import time
from aacommons.dataparser.AirRecorder import LogFileReaderGenerator
from aacommons.dataparser.cli.CliParser import CliParserFactory
from aacommons.dataparser.cli.arcli.ArCliParserRequest import ArCliParserRequest
from aacommons.dataparser.cli.arcli.ArCliContentProvider import ArCliContentProvider


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-.1s <%(module)s> %(funcName)s | %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout', # Default is stderr
        },
        'debug': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "arcli-parser.log",
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10
        }
    },
    'loggers': {
        'aacommons': { 
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': False
        }
    } 
}
logging.config.dictConfig(LOGGING_CONFIG)


def printResultDataRecord(command, record):
    n = list(record.keys())[0]
    d = record[n]
    for dr in d:
        (doc, value) = dr
        print(n, doc, value)


#def printResultDataRecordPandas(command, record):
#    n = list(record.keys())[0]
#    ds = []
#    for d, o in record[n]:
#        _d = {}
#        _d['.document'] = d
#        _d['.timestamp'] = o['timestamp']
#        _d.update(o['body'])
#        ds.append(_d)
#    df = pd.DataFrame(ds)
#    df.attrs = { "name": n, "command": command }
#    print("TABLE", n, df.attrs)
#    print(df.to_string())
#    print("-")


def printResultDataRecords(command, records, f):
    for record in records:
        f(command, record)


def printResultData(command, rd):
    if 'regexes_entire' in rd:
        printResultDataRecords(command, rd['regexes_entire'], printResultDataRecord)
#        printResultDataRecords(command, rd['regexes_entire'], printResultDataRecordPandas)
    if 'tables' in rd:
        printResultDataRecords(command, rd['tables'], printResultDataRecord)
#        printResultDataRecords(command, rd['tables'], printResultDataRecordPandas)
    if 'regexes_byline' in rd:
        printResultDataRecords(command, rd['regexes_byline'], printResultDataRecord)
#        printResultDataRecords(command, rd['regexes_byline'], printResultDataRecordPandas)


def formatAsJson(r, outputFormat, default=None):
    if "jsonl" in outputFormat:
        return json.dumps(r)
    elif "json" in outputFormat:
        return json.dumps(r, indent=2)
    else:
        return default


def printResult(r, indent, outputFormat="text"):
    (command, resultData) = r
    jsonBlob = formatAsJson(r, outputFormat)
    if jsonBlob is not None:
        print(jsonBlob)
        return
    if isinstance(resultData, dict) or resultData is None:
        # Terminal node
        print(indent, command, "->", str(resultData)[0:60], "...", str(resultData)[-40:])
        if resultData is not None:
            printResultData(command, resultData)
    elif isinstance(resultData, list):
        print(indent, command)
        for rd in resultData:
            printResult(rd, indent + "  ")
    else:
        raise Exception("not a tuple or list")


def parseContent(documents, label, command, content, arlog, toStdout=True, outputFormat="text", **kwargs):
    devMode = kwargs.get('dev', False)
    dos2unix = kwargs.get('dos2unix', False)

    # notify
    if devMode:
        print("Dev mode is on, exceptions will raise")

    # Instantiate parser
    contentProvider = ArCliContentProvider(documents)
    cliParser = CliParserFactory.getParser("ARCLI", arCliConfig=contentProvider)

    if arlog is not None:
        # AirRecorder log file
        outputResults = ""
        results = LogFileReaderGenerator(arlog)
        for result in results:
            # Parse
            if result.getQuery().getCommand() is None:
                continue
            parserRequest = ArCliParserRequest()
            parserRequest['Source'] = "me"
            parserRequest['Command'] = result.getQuery().getCommand()
            parserRequest['Stdout'] = result.getStdout()
            parserRequest['Label'] = label
            parserRequest['LocalBeginTime'] = result.getLocalBeginTime()
            # raiseOnException=True to avoid silently consuming exceptions
            # which is useful if we are poking around in the guts of aacommons
            parserRequest['_raiseOnException'] = devMode
            parserRequest['_raiseOnNocliCommandDef'] = devMode
            r = cliParser.parse(parserRequest)
            o = outputResult(r, toStdout, outputFormat)
            outputResults += str(o) + "\n"
        return outputResults

    else:
        # Plain CLI output
        f = open(content, 'r', encoding='utf8', errors='ignore')
        content = f.read()
        f.close()
    
        if dos2unix:
            # clean up files that have Windows line endings and other oddities
            content = content.replace('\r', '')
            content = content.replace('^M', '')

        # Parse
        parserRequest = ArCliParserRequest()
        parserRequest['Source'] = "me"
        parserRequest['Command'] = command
        parserRequest['Stdout'] = content
        parserRequest['Label'] = label
        parserRequest['LocalBeginTime'] = time.time()
        # raiseOnException=True to avoid silently consuming exceptions
        # which is useful if we are poking around in the guts of aacommons
        parserRequest['_raiseOnException'] = devMode
        parserRequest['_raiseOnNocliCommandDef'] = devMode
        r = cliParser.parse(parserRequest)
        return outputResult(r, toStdout, outputFormat)


def outputResult(r, toStdout, outputFormat):
    if not toStdout:
        # caller wants the output for their own usage and/or want to silence stdout
        # take into account any requested outputFormats
        return formatAsJson(r, outputFormat, default=r)

    # Print results
    if r is None:
        print("NO RESULT")
    elif isinstance(r, tuple):
        printResult(r, "", outputFormat)
    else:
        print("UNEXPECTED RESULT")

class CLI:
    """ argparse wrapper for a nicer CLI """
    POS = 40
    WIDTH = 120

    def __init__(self):
        p = argparse.ArgumentParser(
            formatter_class=lambda prog: argparse.HelpFormatter(prog, width=CLI.WIDTH, max_help_position=CLI.POS), 
            description=os.path.basename(sys.argv[0]))
        self.p = p

        o = p.add_argument_group('Input Options')
        o.add_argument('-d', '--doc', help='Document file, default is ./arcli.json', default='arcli.json', metavar='FILENAME')

        labels = ['AOS', 'IAP', 'ACX', 'ASW', 'COMWARE']
        o.add_argument('-l', '--label', help=f'Document label, one of {", ".join(labels)}', choices=labels, metavar='LABEL', required=True)
        # Two combinations are supported:
        # --cmd --infile
        # --arlog
        o.add_argument('-c', '--cmd', help='Command to parse', metavar="CMD", required=False)
        o.add_argument('-i', '--infile', help='Input file containing the raw device output', metavar='FILENAME', required=False)
        o.add_argument('--arlog', help='AirRecorder log file containing the device output', metavar='FILENAME', required=False)

        o = p.add_argument_group('Output Options')
        o.add_argument('--json', help='Output will be formatted as JSON', action='store_true')
        o.add_argument('--jsonl', help='Output will be formatted as JSONL (one JSON record per line)', action='store_true')
        o.add_argument('-o', '--outfile', help='Write output to specified filename (instead of stdout)', default=None, metavar='FILENAME')
        o.add_argument('-n', '--no-stdout', help='Don\'t write output to stdout', action='store_true')
        
        o = p.add_argument_group('Debug Options')
        o.add_argument('--dev', help='Development mode (enables various debugging aids)', action='store_true')
        o.add_argument('--dos2unix', help='Try to clean up input files that contain dos/Windows line endings', action='store_true')
        
    def parse(self):
        """ parse and validate (if required) args """

        def help_exit(msg=None):
            if msg:
                print('\n' + msg + '\n')
            self.p.print_help()
            sys.exit()

        args = self.p.parse_args()

        if args.label is None and args.cmd is None and args.infile is None and args.arlog is None:
            # catch the case of the script being run with no args before
            # any error about -d/--doc is thrown
            help_exit()

        if args.arlog is not None and (args.cmd is not None or args.infile is not None):
            help_exit(f'Error: --arlog cannot be combined with --cmd and/or --infile')
        if args.arlog is None and (args.cmd is None or args.infile is None):
            help_exit(f'Error: --cmd and --infile are required')

        # check provided files exists
        if not os.path.exists(args.doc):
            help_exit(f'Error: -d/--doc {args.doc} does not exist')
        
        if args.infile is not None and not os.path.exists(args.infile):
            help_exit(f'Error: -i/--infile {args.infile} does not exist')
        if args.arlog is not None and not os.path.exists(args.arlog):
            help_exit(f'Error: --arlog {args.arlog} does not exist')

        # setup the output format
        if args.json:
            args.outputFormat = 'json'
        elif args.jsonl:
            args.outputFormat = 'jsonl'
        else:
            args.outputFormat = 'text'

        return args

    def parse_as_dict(self):
        """ helper function to convert parse() result into a pure dict """
        return vars(self.parse())


if __name__ == '__main__':

    args = CLI().parse()

    if args.outfile:
        with open(args.outfile, 'w') as f:
            f.write(str(parseContent(args.doc, args.label, args.cmd, args.infile, args.arlog,
                                     toStdout=False, outputFormat=args.outputFormat, 
                                     dev=args.dev, dos2unix=args.dos2unix)))
        print(f'Script output written to {args.outfile}')
    else:
        parseContent(args.doc, args.label, args.cmd, args.infile, args.arlog,
                     toStdout=not args.no_stdout, outputFormat=args.outputFormat, 
                     dev=args.dev, dos2unix=args.dos2unix)
