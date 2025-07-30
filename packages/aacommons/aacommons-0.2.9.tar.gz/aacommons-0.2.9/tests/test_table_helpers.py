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

from aacommons.dataparser.cli.TableHelpers import contentAsListOfDict


# Test nd.transpose
def test_nd_transpose_acx_show_interface_extended():
    f = open("resources/dataparser/cli/acx-show-interface-extended.txt", "r")
    ttext = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 0,
      "data.offset": 2,
      "begin": "(?m)^Statistics ", "end": "(?m)^Error-Statistics "
    }
    # Do transposition
    headerList = []
    rows = contentAsListOfDict(ttext, marker=None, headerList=headerList, tableOptions=tableOptions)
    assert len(headerList) == 2
    assert headerList[0] == 'Statistics'
    assert headerList[1] == 'Value'
    assert len(rows) == 72
    #print("parsed table(transposition): header: %s, rows: %d" % (headerList, len(rows)))
    if len(rows) > 0 and len(headerList) >= 2:
        # Transposition only makes sense with two or more columns
        nrows = []
        for k in headerList[1:]:
            nrow = {}
            nrow[headerList[0]] = k
            for r in rows:
                nrow[r[headerList[0]]] = r[k]
            nrows.append(nrow)
    assert len(nrows) == 1
    #print(nrows[0].keys())
    assert len(nrows[0].keys()) == 73
    assert nrows[0]['Ethernet Stats Broadcast Packets'] == '8761430'
    assert nrows[0]['If Hc In Broadcast Packets'] == '8531558'
    assert nrows[0]['TX Jumbos'] == '1348148903'
    assert nrows[0]['TX Pause'] == '0'

# Test nd.transpose
def test_nd_transpose_iap_show_ap_debug_radius_statistics():
    f = open("resources/dataparser/cli/iap_show_ap_debug_radius-statistics.txt", "r")
    ttext = f.read()
    f.close()
    tableOptions = {
      "parser": "aos-std"
    }
    # Do transposition
    headerList = []
    rows = contentAsListOfDict(ttext, marker=None, headerList=headerList, tableOptions=tableOptions)
    assert len(headerList) == 3
    assert headerList[0] == 'Statistics'
    assert headerList[1] == 'InternalServer'
    assert headerList[2] == '__gw_192.168.0.1'
    assert len(rows) == 29
    #print("parsed table(transposition): header: %s, rows: %d" % (headerList, len(rows)))
    if len(rows) > 0 and len(headerList) >= 2:
        # Transposition only makes sense with two or more columns
        nrows = []
        for k in headerList[1:]:
            nrow = {}
            nrow[headerList[0]] = k
            for r in rows:
                nrow[r[headerList[0]]] = r[k]
            nrows.append(nrow)
    assert len(nrows) == 2
    assert nrows[0].keys() == nrows[1].keys()
    assert len(nrows[0].keys()) == 30
    assert nrows[0]['In Service: Internet'] == 'Up 11213729s(Not used)'
    assert nrows[1]['In Service: Internet'] == 'Up 7660465s(Not used)'
    assert nrows[0]['Accounting Requests'] == '0'
    assert nrows[1]['Accounting Requests'] == '393884'
    assert nrows[0]['Access-Accept'] == '0'
    assert nrows[1]['Access-Accept'] == '2077'
    assert nrows[0]['SEQ total/free'] == '0/0'
    assert nrows[1]['SEQ total/free'] == '255/255'
