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
# Abstract table parser.
#
# Authors: Thomas Bastian
#
'''

'''
# Parameters
'''
'''
#
'''

import logging


# Logger
log = logging.getLogger(__name__)


class AbstractTableParser():
    def __init__(self):
        self.tables = [{}]
        self.contentLines = []

    def process(self):
        self.preProcess()
        self.readContent()
        self.parse()
        self.postProcess()

    def preProcess(self):
        pass

    def readContent(self):
        pass

    def parse(self):
        pass

    def postProcess(self):
        pass

    def getTables(self):
        return self.tables

    def createPage(self, table, line, header):
        log.debug("table: [%s], line: [%s], header: [%s]" % (table, line, header))
        page = []
        begin = 0
        i = 0
        while i < len(line):
            while (i < len(line)) and (line[i] == '-'):
                i += 1
                continue
            while (i < len(line)) and (line[i] == ' '):
                i += 1
                continue
            column = { 'begin': begin, 'end': i, 'title': header[begin:i] }
            page.append(column)
            begin = i
        return page

    def createRow(self, current, currentPage, tableOptions=None):
        fixShiftedLines = \
            tableOptions is None or \
            (tableOptions is not None and tableOptions.get("fix.shifted.lines", True))
        row = []
        columnNo = 1
        columnCount = len(currentPage)
        for headerColumn in currentPage:
            try:
                beginIndex = headerColumn['begin']
                endIndex = headerColumn['end']
                clen = len(current)
                if clen <= beginIndex:
                    # Not enough characters, generate empty string
                    endIndex = beginIndex = 0
                elif clen <= endIndex:
                    # Not enough characters for this column
                    endIndex = clen
                else:
                    if columnNo == columnCount:
                        # Last column eats everything up
                        endIndex = clen
                value = current[beginIndex:endIndex]
                # Various hacks and workarounds
                if fixShiftedLines and \
                   (columnNo != columnCount) and (value[-1:] != " "):
                    # Last character should be a blank really
                    # Session idx Source IP         Destination IP  Prot SPort Dport Cntr Prio ToS Age Destination TAge Packets Bytes App                        Webcat                    WebRep Packets Bytes PktsDpi PktsAppMoni Flags  Offload flags DPIFlags
                    # ----------- ----------------  --------------  ---- ----- ----- ---- ---- --- --- ----------- ---- ------- ----- -------------------------- ------------------------- ------ ------- ----- ------- ----------- ------ ------------- ---------
                    # 2093        DC:71:96:D8:D6:7D               0806             0    0    0   0   dev20       b7   2       1000  App-Not-Class       [0   ] Web-Not-Class       [0  ] 0      2       1000  0       0           F
                    # 9744        192.168.254.34    192.168.254.30  17   8211  8211  0    0    40  0   local       fd7e 7eba4   13b5df5e App-Not-Class       [0   ] Web-Not-Class       [0  ] 0      7eba4   13b5df5e 0       0           F                    blanks = 0
                    log.debug("detecting shifted lines: line: [%s], column: [%s]" % (current, headerColumn))
                    blanks = 0
                    for c in reversed(value):
                        if c == " ":
                            # Stop on first blank
                            break
                        blanks += 1
                    if blanks < (endIndex - beginIndex):
                        # Underflow to the left
                        current_new = current[0:endIndex-blanks] + " " * blanks + current[endIndex-blanks:]
                        log.debug("spacing correction: new: [%s]" % (current_new))
                        current = current_new
                        value = current[beginIndex:endIndex]
                    else:
                        # Overflow to the right
                        overflow = 0
                        for c in current[endIndex:]:
                            if c == " ":
                                break
                            overflow += 1
                        if overflow > 0:
                            current_new = current[0:endIndex] + current[endIndex+overflow+1:]
                            value = current[beginIndex:endIndex+overflow]
                            log.debug("overflow correction: new: [%s]" % (current_new))
                            current = current_new
                        else:
                            log.debug("no overflow correction")
                row.append(value)
            except Exception as e:
                raise Exception(e)
            columnNo += 1
        return row
