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

from aacommons.dataparser.AirRecorder import LogFileReaderGenerator, LogFileProcessor


# Test AirRecorder log file reader
def test_airrecorder1():
    results = LogFileReaderGenerator('resources/dataparser/airrecorder1.txt')
    lresults = list(results)
    assert len(lresults) == 2
    # Header
    result = lresults[0]
    assert result is not None
    # First record
    result = lresults[1]
    assert result is not None
    assert result.getStatus() > 0
    assert result.getQuery() is not None
    assert result.getQuery().getCommand() is not None
    assert result.getQuery().getCommand() == 'display ospfv3 statistics error'
    assert 'OSPFv3 Process 1 with Router ID 172.24.0.1' in result.getStdout()

# Test AirRecorder log file reader
def test_airrecorder2():
    results = LogFileReaderGenerator('resources/dataparser/airrecorder2.txt')
    lresults = list(results)
    assert len(lresults) == 48
    # Header
    result = lresults[0]
    assert result is not None
    # First record
    result = lresults[1]
    assert result is not None
    assert result.getStatus() > 0
    assert result.getQuery() is not None
    assert result.getQuery().getCommand() is not None
    assert result.getQuery().getCommand() == 'show version'
    assert 'Built: 2012-10-24 13:51:09' in result.getStdout()
    # Last record
    result = lresults[47]
    assert result is not None
    assert result.getStatus() > 0
    assert result.getStatus() == 3175
    assert result.getLocalBeginTime() == 1400082196840
    assert result.getLocalEndTime() == 1400082196904
    assert result.getQuery() is not None
    assert len(result.getQuery().getTags()) == 2
    assert result.getQuery().getTags()['airrecorder.command'] == '0,show ap arm rf-summary ap-name %{ap:name}'
    assert result.getQuery().getTags()['airrecorder.group'] == '5ae99cbb.0003c968d2c1b704'
    assert result.getQuery().getCommand() is not None
    assert result.getQuery().getCommand() == 'show ap arm rf-summary ap-name ap-060440301-001'
    assert '36       0      0        0        93     0/0/0/0/100  0/0(0)          0/0//0/0(0)' in result.getStdout()

class TestLogFileProcessor(LogFileProcessor):
    def __init__(self, fileName):
        super().__init__(fileName)
        self.count = 0

    def processResult(self, command, result):
        self.count += 1

    def getCount(self):
        return self.count

# Test AirRecorder log file processor
def test_airrecorder_processor1():
    processor = TestLogFileProcessor('resources/dataparser/airrecorder2.txt')
    processor.run()
    assert processor.getCount() == 47
