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

from aacommons.dataparser.cli.RowColumnTableParser import RowColumnTableParser


# Test RowColumnTableParser: aos-std
def test_show_ap_active():
    f = open('resources/dataparser/cli/show-ap-active-long.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'aos-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'Active AP Table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 11
    assert header[0]['title'] == "Name                 "
    assert len(rows) == 370
    assert "WH_CR_AP27           " == rows[3][0]
    assert "WH_OPD_AP02          " == rows[62][0]
    assert "WH_FBJ_GF_AP01       " == rows[65][0]
    assert "WH_Floors     " == rows[125][1]
    assert "10.104.111.148  " == rows[128][2]
    assert "0            " == rows[191][3]
    assert "HGH_LAB_AP35_WHCont  " == rows[202][0]
    assert "AP:HT:44+/12/21      " == rows[202][6]
    assert "124      " == rows[259][7]
    assert "AdaK   " == rows[318][8]
    assert "21h:30m:43s  " == rows[321][9]
    assert "N/A" == rows[369][10]

# Test RowColumnTableParser: aos-dp-std
def test_show_datapath_tunnel_table():
    f = open('resources/dataparser/cli/show-datapath-tunnel-table.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'aos-dp-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'Datapath Tunnel Table Entries'
    rows = table['rows']
    header = table['header']
    assert len(header) == 15
    assert header[0]['title'] == " #   "
    assert len(rows) == 9
    assert "14   " == rows[3][0]
    assert "19   " == rows[8][0]
    assert "13   " == rows[1][0]
    assert "10.162.136.108  " == rows[5][1]
    assert "0.2.0.0         " == rows[0][2]
    assert "47   " == rows[5][3]
    assert "0     " == rows[0][4]
    assert "1500  " == rows[5][5]
    assert "0    " == rows[0][6]
    assert "0    0    51   0     " == rows[5][7]
    assert "00:00:00:00:00:00 " == rows[0][8]
    assert "    36343  " == rows[5][9]
    assert "        0  " == rows[0][10]
    assert "        0  " == rows[5][11]
    assert " 28 " == rows[0][12]
    assert "  0 " == rows[5][13]
    assert "T " == rows[0][14]

# Test RowColumnTableParser: aos-dp-std
def test_show_datapath_session_table():
    f = open('resources/dataparser/cli/show-datapath-session-table.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'aos-dp-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'Datapath Session Table Entries'
    rows = table['rows']
    header = table['header']
    assert len(header) == 15
    assert header[0]['title'] == "Source IP or MAC  "
    assert len(rows) == 77
    assert "172.16.16.209     " == rows[3][0]
    assert "172.16.16.209     " == rows[8][0]
    assert "172.16.16.209     " == rows[1][0]
    assert "172.16.16.209   " == rows[5][1]
    assert "17   " == rows[0][2]
    assert "30628 " == rows[5][3]
    assert "8209  " == rows[0][4]
    assert " 0/0     " == rows[5][5]
    assert "0    " == rows[0][6]
    assert "0   " == rows[5][7]
    assert "tunnel 22   " == rows[0][9]
    assert "tunnel 16   " == rows[75][9]
    assert "6603 " == rows[75][10]
    assert "176927     " == rows[75][11]
    assert "57485694   " == rows[75][12]
    assert "FCI             " == rows[75][13]
    assert "7" == rows[75][14]

# Test GenericRegexTableParser: data
def test_show_datapath_utilization():
    f = open('resources/dataparser/cli/show-datapath-utilization.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'generic-regex',
                    'data.regex': '\\s+(?P<cpu>\\d+) \\| \\s+(?P<util1>\\d+)% \\| \\s+(?P<util4>\\d+)% \\| \\s+(?P<util64>\\d+)% \\|',
                    'data.offset': 5 }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'generic regex table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 4
    assert header[0]['title'] == "cpu"
    assert header[1]['title'] == "util1"
    assert header[2]['title'] == "util4"
    assert header[3]['title'] == "util64"
    assert len(rows) == 24
    assert "10" == rows[2][0]
    assert "0" == rows[2][1]
    assert "13" == rows[2][2]
    assert "0" == rows[2][3]
    assert "11" == rows[3][0]
    assert "0" == rows[3][1]
    assert "0" == rows[3][2]
    assert "24" == rows[3][3]
    assert "31" == rows[23][0]
    assert "0" == rows[23][1]
    assert "0" == rows[23][2]
    assert "0" == rows[23][3]

# Test GenericRegexTableParser: header.regex
def test_show_airmatch_optimization():
    f = open("resources/dataparser/cli/show-airmatch-optimization.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 0,
      "header.regex": "(?P<Seq>Seq +)(?P<Time>Time +)(?P<APs> APs +)(?P<FiveGRadios>5GHz Radios +)(?P<TwoFourGRadios>2GHz Radios +)(?P<Type>Type) *",
      "data.offset": 2
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 6
    rows = table['rows']
    assert len(rows) == 145
    assert rows[0][0] == "#4941 "
    assert rows[0][1] == "2020-07-27_07:00:08   "
    assert rows[0][2] == "  112  "
    assert rows[0][3] == "        112 "
    assert rows[0][4] == "        112 "
    assert rows[0][5] == "Scheduled"
    assert rows[144][0] == "#4797 "
    assert rows[144][1] == "2020-06-26_15:00:56   "
    assert rows[144][2] == "   44  "
    assert rows[144][3] == "         44 "
    assert rows[144][4] == "         43 "
    assert rows[144][5] == "Scheduled"

# Test GenericRegexTableParser: header.split
def test_generic_regex_header_split():
    f = open("resources/dataparser/cli/generic-regex-header-split.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 3,
      "data.offset": 4
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 3
    rows = table['rows']
    assert len(rows) == 2
    assert rows[0][0] == 'R1CA       '
    assert rows[0][1] == 'R1CB      BBBB        '
    assert rows[0][2] == 'R1CC        X'
    assert rows[1][0] == 'R2CA   AAA '
    assert rows[1][1] == 'R2CB B B B            '
    assert rows[1][2] == 'R2CC C C '

# Test GenericRegexTableParser: header.split
def test_generic_regex_header_split_acx_show_interface_extended():
    f = open("resources/dataparser/cli/acx-show-interface-extended.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 0,
      "data.offset": 2,
      "begin": "(?m)^Statistics ", "end": "(?m)^Error-Statistics "
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 2
    rows = table['rows']
    assert len(rows) == 72
    assert rows[0][0] == 'Dot3 In Pause Frames                           '
    assert rows[0][1] == '0 '
    assert rows[2][0] == 'Ethernet Stats Broadcast Packets               '
    assert rows[2][1] == '8761430 '
    assert rows[11][0] == 'Ethernet Stats Packets 512 To 1023 Bytes       '
    assert rows[11][1] == '315931713 '
    assert rows[66][0] == 'TX Bytes                                       '
    assert rows[66][1] == '2529615062836 '
    assert rows[70][0] == 'TX Packets                                     '
    assert rows[70][1] == '3495768628 '
    assert rows[71][0] == 'TX Pause                                       '
    assert rows[71][1] == '0 '

# Test GenericRegexTableParser: data.regex
def test_generic_regex_comware():
    f = open("resources/dataparser/cli/debug_rxtx_softcar.txt", "r", newline="\n")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "data.offset": 1,
      "data.regex": "^(?P<ID>\\d+) +(?P<Type>[ \\w\\d\\/\\.]{1,19}) +(?P<RcvPps>\\d+) +(?P<RcvAll>\\d+) +(?P<DisPktAll>\\d+) +(?P<Pps>\\d+) +(?P<Dyn>\\S+) +(?P<Swi>\\S+) +(?P<Hash>\\S+) +(?P<ACLmax>\\d+)"
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    header = table['header']
    assert len(header) == 10
    assert header[0]['title'] == "ID"
    assert header[2]['title'] == "RcvPps"
    assert header[3]['title'] == "RcvAll"
    assert header[6]['title'] == "Dyn"
    assert header[9]['title'] == "ACLmax"
    rows = table['rows']
    assert len(rows) == 126
    assert rows[0][0] == '0'
    assert rows[0][1] == 'ROOT               '
    assert rows[0][5] == '1000'
    assert rows[0][6] == 'S'
    assert rows[1][0] == '1'
    assert rows[1][1] == 'ISIS               '
    assert rows[1][5] == '2000'
    assert rows[1][6] == 'D'
    assert rows[5][1] == 'UNKNOWN_IPV4MC     '
    assert rows[5][5] == '300'
    assert rows[5][6] == 'S'
    assert rows[124][1] == 'FTP_CTRL           '
    assert rows[124][5] == '300'
    assert rows[124][6] == 'S'
    assert rows[125][1] == 'ROUTE TO CPU MASK  '
    assert rows[125][5] == '200'
    assert rows[125][6] == 'S'

# Test GenericJsonCsvTableParser: seashell output
def test_generic_json_csv_seashell():
    f = open("resources/dataparser/cli/seashell_show_devices.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-json-csv"
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic json csv table'
    header = table['header']
    assert len(header) == 8
    assert header[0]['title'] == "Type"
    assert header[2]['title'] == "Group"
    assert header[3]['title'] == "Serial"
    assert header[6]['title'] == "IP"
    assert header[7]['title'] == "Model"
    rows = table['rows']
    assert len(rows) == 8
    assert rows[0][0] == 'GATEWAY'
    assert rows[0][1] == 'Aruba7005-3_11_E7_B8'
    assert rows[0][5] == 'Down'
    assert rows[0][6] == '172.30.0.1'
    assert rows[1][0] == 'GATEWAY'
    assert rows[1][1] == 'Aruba9004-1_B5_86_BA'
    assert rows[1][5] == 'Down'
    assert rows[1][6] == '172.30.0.3'
    assert rows[5][0] == 'IAP'
    assert rows[5][1] == '94:b4:0f:c1:a2:e4'
    assert rows[5][7] == 'AP-225'
    assert rows[6][1] == 'A2930F-DC1'
    assert rows[6][2] == 'asw1'
    assert rows[6][4] == '98:f2:b3:bf:3d:10'
    assert rows[7][1] == 'Aruba-2930F-8G-PoEP-2SFPP'
    assert rows[7][5] == 'Down'
    assert rows[7][6] == '100.127.1.10'

# Test GenericRegexTableParser: header.regex with begin
def test_show_airmatch_optimization_begin():
    f = open("resources/dataparser/cli/show-airmatch-optimization-begin.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 2,
      "header.regex": "(?P<Seq>Seq +)(?P<Time>Time +)(?P<APs> APs +)(?P<FiveGRadios>5GHz Radios +)(?P<TwoFourGRadios>2GHz Radios +)(?P<Type>Type) *",
      "data.offset": 4,
      "begin": "(?m)^BEGIN==="
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 6
    rows = table['rows']
    assert len(rows) == 145
    assert rows[0][0] == "#4941 "
    assert rows[0][1] == "2020-07-27_07:00:08   "
    assert rows[0][2] == "  112  "
    assert rows[0][3] == "        112 "
    assert rows[0][4] == "        112 "
    assert rows[0][5] == "Scheduled"
    assert rows[144][0] == "#4797 "
    assert rows[144][1] == "2020-06-26_15:00:56   "
    assert rows[144][2] == "   44  "
    assert rows[144][3] == "         44 "
    assert rows[144][4] == "         43 "
    assert rows[144][5] == "Scheduled"

# Test GenericRegexTableParser: header.regex with end
def test_show_airmatch_optimization_end():
    f = open("resources/dataparser/cli/show-airmatch-optimization-end.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 0,
      "header.regex": "(?P<Seq>Seq +)(?P<Time>Time +)(?P<APs> APs +)(?P<FiveGRadios>5GHz Radios +)(?P<TwoFourGRadios>2GHz Radios +)(?P<Type>Type) *",
      "data.offset": 2,
      "end": "(?m)^END==="
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 6
    rows = table['rows']
    assert len(rows) == 145
    assert rows[0][0] == "#4941 "
    assert rows[0][1] == "2020-07-27_07:00:08   "
    assert rows[0][2] == "  112  "
    assert rows[0][3] == "        112 "
    assert rows[0][4] == "        112 "
    assert rows[0][5] == "Scheduled"
    assert rows[144][0] == "#4797 "
    assert rows[144][1] == "2020-06-26_15:00:56   "
    assert rows[144][2] == "   44  "
    assert rows[144][3] == "         44 "
    assert rows[144][4] == "         43 "
    assert rows[144][5] == "Scheduled"

# Test GenericRegexTableParser: header.regex with begin and end
def test_show_airmatch_optimization_begin_end():
    f = open("resources/dataparser/cli/show-airmatch-optimization-begin-end.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "generic-regex",
      "header.offset": 2,
      "header.regex": "(?P<Seq>Seq +)(?P<Time>Time +)(?P<APs> APs +)(?P<FiveGRadios>5GHz Radios +)(?P<TwoFourGRadios>2GHz Radios +)(?P<Type>Type) *",
      "data.offset": 4,
      "begin": "(?m)^BEGIN===",
      "end": "(?m)^END==="
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    assert table['name'] == 'generic regex table'
    assert len(table['header']) == 6
    rows = table['rows']
    assert len(rows) == 145
    assert rows[0][0] == "#4941 "
    assert rows[0][1] == "2020-07-27_07:00:08   "
    assert rows[0][2] == "  112  "
    assert rows[0][3] == "        112 "
    assert rows[0][4] == "        112 "
    assert rows[0][5] == "Scheduled"
    assert rows[144][0] == "#4797 "
    assert rows[144][1] == "2020-06-26_15:00:56   "
    assert rows[144][2] == "   44  "
    assert rows[144][3] == "         44 "
    assert rows[144][4] == "         43 "
    assert rows[144][5] == "Scheduled"

# Test AOS smart multi-table
def test_show_datapath_l3_interface_smart():
    f = open("resources/dataparser/cli/show-datapath-l3-interface-smart.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "aos-smart",
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 2
    # First table
    table = tables[0]
    assert table['name'] == 'L3Interface'
    assert len(table['header']) == 4
    titles = []
    type_hints = []
    for h in table['header']:
        titles.append(h['title'])
        type_hints.append(h['type_hint'])
    assert (titles == ["Idx","InterfaceIP","GatewayIp","NATIp"])
    assert (type_hints == ["bigint","inet","inet","inet"])
    rows = table['rows']
    assert len(rows) == 1
    assert rows[0][0] == "1"
    assert rows[0][1] == "10.1.101.34"
    assert rows[0][2] == "10.1.101.1"
    assert rows[0][3] == "0.0.0.0"
    # Second table
    table = tables[1]
    assert table['name'] == 'VUplinkNhInfo'
    assert len(table['header']) == 2
    titles = []
    type_hints = []
    for h in table['header']:
        titles.append(h['title'])
        type_hints.append(h['type_hint'])
    assert (titles == ["Vlan","GatewayIp"])
    assert (type_hints == ["integer","inet"])
    rows = table['rows']
    assert len(rows) == 0

# Test AOS smart multi-table
def test_show_datapath_l3_interface_smart_with_id():
    f = open("resources/dataparser/cli/show-datapath-l3-interface-smart.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "aos-smart", "aos.smart.table.#": 2
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    # First table
    table = tables[0]
    assert table['name'] == 'VUplinkNhInfo'
    assert len(table['header']) == 2
    titles = []
    type_hints = []
    for h in table['header']:
        titles.append(h['title'])
        type_hints.append(h['type_hint'])
    assert (titles == ["Vlan","GatewayIp"])
    assert (type_hints == ["integer","inet"])
    rows = table['rows']
    assert len(rows) == 0

# Test AOS smart single-table
def test_show_datapath_route_cache_smart():
    f = open("resources/dataparser/cli/show-datapath-route-cache-smart.txt", "r")
    content = f.read()
    f.close()
    tableOptions = {
      "parser": "aos-smart",
    }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    table = tables[0]
    assert len(tables) == 1
    titles = []
    type_hints = []
    for h in table['header']:
        titles.append(h['title'])
        type_hints.append(h['type_hint'])
    assert (titles == ["IP","MAC","VLAN","RCI","RCV","PRTI","PRTV","Flags"])
    assert (type_hints == ["inet","macaddr","text","bigint","bigint","bigint","bigint","text"])
    assert table['name'] == 'RouteCache'
    assert len(table['header']) == 8
    rows = table['rows']
    assert len(rows) == 11
    assert rows[0][0] == "172.20.108.1"
    assert rows[0][1] == "dc:a6:32:63:05:8f"
    assert rows[0][2] == "108"
    assert rows[0][3] == "7"
    assert rows[0][4] == "13"
    assert rows[0][5] == "0"
    assert rows[0][6] == "0"
    assert rows[0][7] == "tA"
    assert rows[10][0] == "172.16.16.221"
    assert rows[10][1] == "00:00:00:00:00:00"
    assert rows[10][2] == "0"
    assert rows[10][3] == "9"
    assert rows[10][4] == "17"
    assert rows[10][5] == "35"
    assert rows[10][6] == "47"
    assert rows[10][7] == "PIl"
    assert rows[6][0] == "172.27.10.2"
    assert rows[6][1] == "00:00:00:00:00:00"
    assert rows[6][2] == "0"
    assert rows[6][3] == "11"
    assert rows[6][4] == "700"
    assert rows[6][5] == "13"
    assert rows[6][6] == "11"
    assert rows[6][7] == "N"

# Test RowColumnTableParser: aos-std with shifted lines
def test_show_airgroup_cache_entries_shifted():
    f = open('resources/dataparser/cli/show-airgroup-cache-entries-shifted.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'aos-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'Cache Entries'
    rows = table['rows']
    header = table['header']
    assert len(header) == 7
    assert header[0]['title'] == "Name                                                 "
    assert len(rows) == 25
    assert "_rdlink._tcp.local                                   " == rows[0][0]
    assert "PTR         " == rows[0][1]
    assert "IN     " == rows[0][2]
    assert "4500  " == rows[0][3]
    assert "192.168.254.65   " == rows[0][4]
    assert "foreign  " == rows[0][5]
    assert "Tue Dec 27 11:26:40 2022" == rows[0][6]
    assert "Marnie’s iPad._companion-link._tcp.local             " == rows[6][0]
    assert "TXT         " == rows[6][1]
    assert "Tue Dec 27 11:22:05 2022" == rows[6][6]
    assert "Marnie’s iPad._companion-link._tcp.local             " == rows[7][0]
    assert "SRV/NBSTAT  " == rows[7][1]
    assert "Tue Dec 27 11:22:05 2022" == rows[7][6]
    assert "🅱️ ._rdlink._tcp.local                               " == rows[24][0]
    assert "TXT         " == rows[24][1]
    assert "Tue Dec 27 11:27:52 2022" == rows[24][6]

# Test RowColumnTableParser: aos-std with shifted lines
def test_show_datapath_session_dpi_verbose_shifted():
    f = open('resources/dataparser/cli/show-datapath-session-dpi-verbose-shifted.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'aos-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'Datapath Session Table Entries'
    rows = table['rows']
    header = table['header']
    assert len(header) == 24
    assert header[0]['title'] == "Session idx "
    assert header[1]['title'] == "Source IP         "
    assert header[2]['title'] == "Destination IP  "
    assert header[3]['title'] == "Prot "
    assert header[4]['title'] == "SPort "
    assert header[5]['title'] == "Dport "
    assert header[6]['title'] == "Cntr "
    assert header[7]['title'] == "Prio "
    assert header[8]['title'] == "ToS "
    assert header[9]['title'] == "Age "
    assert header[10]['title'] == "Destination "
    assert header[11]['title'] == "TAge "
    assert header[12]['title'] == "Packets "
    assert header[13]['title'] == "Bytes "
    assert header[14]['title'] == "App                        "
    assert header[15]['title'] == "Webcat                    "
    assert header[16]['title'] == "WebRep "
    assert header[17]['title'] == "Packets "
    assert header[18]['title'] == "Bytes "
    assert header[19]['title'] == "PktsDpi "
    assert header[20]['title'] == "PktsAppMoni "
    assert header[21]['title'] == "Flags  "
    assert header[22]['title'] == "Offload flags "
    assert header[23]['title'] == "DPIFlags "
    assert len(rows) == 7
    assert "2093        " == rows[1][0]
    assert "DC:71:96:D8:D6:7D " == rows[1][1]
    assert "                " == rows[1][2]
    assert "0806 " == rows[1][3]
    assert "dev20       " == rows[1][10]
    assert "F      " == rows[1][21]
    assert "9744        " == rows[3][0]
    assert "192.168.254.34    " == rows[3][1]
    assert "192.168.254.30  " == rows[3][2]
    assert "17   " == rows[3][3]
    assert "local       " == rows[3][10]
    assert "App-Not-Class       [0   ] " == rows[3][14]
    assert "Web-Not-Class       [0  ] " == rows[3][15]
    assert "7eba4   " == rows[3][17]
    assert "13b5df5e" == rows[3][18]
    assert "F      " == rows[3][21]
    assert "9748        " == rows[5][0]
    assert "192.168.254.32    " == rows[5][1]
    assert "192.168.254.30  " == rows[5][2]
    assert "17   " == rows[5][3]
    assert "dev3        " == rows[5][10]
    assert "dns                 [32  ] " == rows[5][14]
    assert "Web-Not-Class       [0  ] " == rows[5][15]
    assert "17df2f  " == rows[5][17]
    assert "241fff75" == rows[5][18]
    assert "FC     " == rows[5][21]
