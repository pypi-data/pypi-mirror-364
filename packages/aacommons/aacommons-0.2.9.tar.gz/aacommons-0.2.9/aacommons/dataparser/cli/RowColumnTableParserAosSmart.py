#
# Copyright 2022 Thomas Bastian, Jeffrey Goff, Albert Pang
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
# Standard AOS smart row/column table parser.
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

import json
import logging
import re
from .AbstractTableParser import AbstractTableParser


# Logger
log = logging.getLogger(__name__)


#
# Global value converters
#

# Convert hex value to int
def vc_hex(value_in):
    value_out = int(value_in, 16)
    return str(value_out)

# Value converters by type
valueConvertersByType = {
    "hex": ("bigint", vc_hex),
}


class RowColumnTableParserAosSmart(AbstractTableParser):
    def __init__(self, source, tableOptions):
        super().__init__()
        self.source = source
        self.tableNum = tableOptions.get("aos.smart.table.#", 0)

    def readContent(self):
        if type(self.source) == list:
            raise Exception("not supported")

    def createPage(self, table, header):
        log.debug("table: [%s], header: [%s]" % (table, header))
        page = []
        for h in header:
            column = { 'begin': 0, 'end': 0, 'title': h }
            page.append(column)
        return page

    def parseJSON(self, jsonText):
        #log.debug("JSON text [%s]" % jsonText)
        jsonData = json.loads(jsonText)

        # Update main table
        current_table = {}
        self.tables.append(current_table)
        tname = jsonData["dbname"].strip()
        current_table['name'] = tname
        log.debug("processing table [%s]" % str(tname))

        header = jsonData["header"]
        current_table['header'] = self.createPage(current_table, header)

        # Value converters
        header_types = jsonData["schema"]["header_types"]
        value_converters = {}
        vci = 0
        for ht in header_types:
            (value_type_hint, value_converter) = valueConvertersByType.get(ht, (None, None))
            if value_converter is not None:
                value_converters[vci] = value_converter
                current_table['header'][vci]['type_hint'] = value_type_hint
            else:
                current_table['header'][vci]['type_hint'] = ht
            vci += 1
        log.debug("type_hint: [%s], header: [%s]" % (current_table, header))

        rows = []
        for entry in jsonData["entries"]:
            if len(entry) == 0:
                # Skip empty arrays
                continue
            if len(entry) != len(header):
                raise Exception("bad header vs row")
            if len(value_converters) > 0:
                # Convert some columns
                for k, v in value_converters.items():
                    entry[k] = v(entry[k])
            rows.append(entry)
        current_table['rows'] = rows
        log.debug("processed table [%s] rows [%d]" % (str(tname), len(rows)))

    def parse(self):
        # Process all JSON objects
        self.tables = []
        json_offset = 0
        table_num = 1
        while True:
            log.debug("searching JSON object: @[%d]" % (json_offset))
            cb_start_match =  re.search("^{", self.source[json_offset:], flags=re.MULTILINE)
            if cb_start_match is None:
                # No more JSON objects
                break
            cb_end_match =  re.search("^}", self.source[json_offset:], flags=re.MULTILINE)
            if cb_end_match is None:
                raise Exception("malformed JSON object")
            log.debug("found JSON object: @[%d]:[%d]:[%d]" % (json_offset, cb_start_match.start(), cb_end_match.end()))
            if (self.tableNum <= 0) or (table_num == self.tableNum):
                self.parseJSON(self.source[json_offset + cb_start_match.start():json_offset + cb_end_match.end()])
                if (table_num == self.tableNum):
                    break
            json_offset += cb_end_match.end()
            table_num += 1
        log.debug("processed [%d] tables" % (len(self.tables)))
