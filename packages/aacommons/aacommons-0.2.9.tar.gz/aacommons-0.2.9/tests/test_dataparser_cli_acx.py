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


# Test RowColumnTableParser: acx-std
def test_show_interface_link_status():
    f = open('resources/dataparser/cli/acx-show-interface-link-status.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'acx-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'standard acx table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 4
    assert header[0]['title'] == "Port"
    assert len(rows) == 9
    assert "1/1/4     " == rows[3][0]
    assert "1GbT            " == rows[3][1]
    assert "up          " == rows[3][2]
    assert "15" == rows[3][3]
    assert "1/1/9     " == rows[8][0]
    assert "1GbT            " == rows[8][1]
    assert "up          " == rows[8][2]
    assert "661" == rows[8][3]

# Test RowColumnTableParser: acx-std
def test_show_environment_power_supply():
    f = open('resources/dataparser/cli/acx-show-environment-power-supply.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'acx-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'standard acx table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 7
    assert header[0]['title'] == "Mbr/PSU"
    assert len(rows) == 1
    assert "1/1      " == rows[0][0]
    assert "N/A      " == rows[0][1]
    assert "N/A               " == rows[0][2]
    assert "OK             " == rows[0][3]
    assert "AC      " == rows[0][4]
    assert "100V-240V  " == rows[0][5]
    assert "500" == rows[0][6]

# Test RowColumnTableParser: acx-std
def test_show_vlan():
    f = open('resources/dataparser/cli/acx-show-vlan.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'acx-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'standard acx table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 6
    assert header[0]['title'] == "VLAN"
    assert len(rows) == 2
    assert "1     " == rows[0][0]
    assert "DEFAULT_VLAN_1                    " == rows[0][1]
    assert "up      " == rows[0][2]
    assert "ok                      " == rows[0][3]
    assert "default     " == rows[0][4]
    assert "1/1/1-1/1/52" == rows[0][5]

# Test RowColumnTableParser: acx-std
def test_show_environment_led():
    f = open('resources/dataparser/cli/acx-show-environment-led.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'acx-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'standard acx table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 3
    assert header[0]['title'] == "Mbr/Name"
    assert len(rows) == 1
    assert "1/locator      " == rows[0][0]
    assert "off          " == rows[0][1]
    assert "ok" == rows[0][2]

# Test RowColumnTableParser: acx-std
def test_show_interface_brief():
    f = open('resources/dataparser/cli/acx-show-interface-brief.txt', 'r')
    content = f.read()
    f.close()
    tableOptions = { 'parser': 'acx-std' }
    p = RowColumnTableParser(content, tableOptions=tableOptions)
    p.process()
    tables = p.getTables()
    assert len(tables) == 1
    table = tables[0]
    assert table['name'] == 'standard acx table'
    rows = table['rows']
    header = table['header']
    assert len(header) == 8
    assert header[0]['title'] == "Port"
    assert len(rows) == 16
    assert "1/1/1     " == rows[0][0]
    assert "1       " == rows[0][1]
    assert "access " == rows[0][2]
    assert "1GbT           " == rows[0][3]
    assert "yes     up      " == rows[0][4]
    assert "                       " == rows[0][5]
    assert "1000    " == rows[0][6]
    assert "--" == rows[15][7]
    assert "1/1/16    " == rows[15][0]
    assert "1       " == rows[15][1]
    assert "access " == rows[15][2]
    assert "1GbT           " == rows[15][3]
    assert "yes     up      " == rows[15][4]
    assert "                       " == rows[15][5]
    assert "100     " == rows[15][6]
    assert "--" == rows[15][7]
