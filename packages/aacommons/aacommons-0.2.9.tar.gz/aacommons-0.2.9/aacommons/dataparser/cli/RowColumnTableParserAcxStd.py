#
# Copyright 2020 Thomas Bastian, Jeffrey Goff, Albert Pang
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
# Standard ACX row/column table parser.
#
# Authors: Thomas Bastian
#
# Parses following tables:
#
-------------------------------------------------
Port      Type            Physical    Link
                          Link State  Transitions
-------------------------------------------------
<data>

------------------------------------------------------------------------------
         Product  Serial            PSU            Input   Voltage    Wattage
Mbr/PSU  Number   Number            Status         Type    Range      Maximum
------------------------------------------------------------------------------
<data>

Mbr/Name       State        Status
----------------------------------
<data>

Prefix               Nexthop           Interface     VRF(egress)   Origin/  Distance/    Age
                                                                   Type     Metric
-----------------------------------------------------------------------------------------------------
<data>

#
'''

'''
# Parameters
'''
'''
#
'''

import logging
import re
from .AbstractTableParser import AbstractTableParser


# Logger
log = logging.getLogger(__name__)


class RowColumnTableParserAcxStd(AbstractTableParser):
    def __init__(self, source, tableOptions=None):
        super().__init__()
        self.source = source
        self.tableOptions = tableOptions
        self.marker = "--------"
        self.markerSearchLines = 10
        self.stopOnEmptyLine = True
        if tableOptions is not None:
            self.marker = tableOptions.get("marker", self.marker)
            self.markerSearchLines = tableOptions.get("marker.search.lines", self.markerSearchLines)
            self.stopOnEmptyLine = tableOptions.get("stop.on.empty.line", self.stopOnEmptyLine)

    def readContent(self):
        if type(self.source) == list:
            self.contentLines = self.source
        else:
            self.contentLines = self.source.splitlines()

    def createPositionalColumnsFromSplit(self, splitRegex, line):
        splits = re.split(splitRegex, line.rstrip())
        columns = []
        i = 0
        for split in splits:
            column = { 'title': split, 'begin': line.index(split) }
            if (i + 1) < len(splits):
                # Not last column
                column['end'] = line.index(splits[i + 1])
            columns.append(column)
            i += 1
        log.debug("columns: [%s]" % (columns))
        return columns

    def parse(self):
        log.debug("marker [%s], marker.search.lines: %d" % (str(self.marker), self.markerSearchLines))
        currentLineNo = -1
        seenMarker = False
        mainColumns = None
        for currentLine in self.contentLines:
            currentLineNo += 1
            if not seenMarker:
                if (currentLineNo > self.markerSearchLines):
                    raise Exception("marker not found in %d lines" % (self.markerSearchLines))
                if currentLine.strip() == '' or currentLine.startswith(self.marker):
                    # Skip empty lines or <marker>
                    continue
                else:
                    # First non empty line
                    seenMarker = True
            if seenMarker:
                if currentLine.startswith(self.marker):
                    # End of header
                    currentLineNo += 1
                    break
                currentColumns = self.createPositionalColumnsFromSplit('  +', currentLine)
                if mainColumns is None:
                    mainColumns = currentColumns
                    continue
                else:
                    # Enhance using secondary lines
                    for c in currentColumns:
                        if c['title'] == '':
                            continue
                        for mc in mainColumns:
                            if 'begin' in c and 'begin' in mc and c['begin'] == mc['begin']:
                                # Begin matches. Optional end if present matches
                                if ('end' in c and 'end' in mc and c['end'] == mc['end']) or \
                                   ('end' not in c):
                                    # Append title
                                    if mc['title'] == '':
                                        mc['title'] = c['title']
                                    elif mc['title'].endswith('/'):
                                        mc['title'] += c['title']
                                    else:
                                        mc['title'] += ' ' + c['title']

        if mainColumns is None:
            raise Exception("no heading found")

        # Update main table
        self.tables[0]['name'] = "standard acx table"
        log.debug("processing table with headings [%s]" % (mainColumns))

        rows = []
        self.tables[0]['rows'] = rows
        self.tables[0]['header'] = mainColumns
        while currentLineNo < len(self.contentLines):
            currentLine = self.contentLines[currentLineNo]
            if currentLine.strip() == "":
                if self.stopOnEmptyLine:
                    break
                else:
                    currentLineNo += 1
                    continue

            dataRow = []
            for column in mainColumns:
                value = ""
                begin = column['begin']
                if begin < 0:
                    # Should never happen
                    begin = 0
                end = column.get('end', -1)
                if end < 0:
                    # Unset end means until end of line
                    end = len(currentLine)
                if begin < len(currentLine):
                    value = currentLine[begin:min(end, len(currentLine))]
                dataRow.append(value)
            rows.append(dataRow)

            currentLineNo += 1
