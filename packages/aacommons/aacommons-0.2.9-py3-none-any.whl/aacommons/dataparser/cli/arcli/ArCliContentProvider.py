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
# ArCliContentProvider
#
# Provides ARCLI content through getContent()
#
# Authors: Thomas Bastian
#
'''

import jstyleson
import logging
import os
from ....contentprovider.ContentProvider import ContentProvider
import zipfile


# Logger
log = logging.getLogger(__name__)


#
# Reads from all-in-one arcli.json and/or from filesystem
# Expects following file-system structure
#
# arcli.json (filename)
# <class>/
#   <qualifier>/
#     <JSON file with document definition(s)
#     ...
#
# where <class> is one of ACX, AOS, ASW, COMWARE, IAP
# <class>/<qualifier> is the "label", i.e. AOS/default
#
class ArCliFilesystemContentProvider(ContentProvider):
    def __init__(self, filename):
        self.filename = filename
        self.basepath = os.path.dirname(filename)

    def __str__(self):
        return "file://" + self.filename

    def _readContent(self, filename):
        with open(filename, 'r', encoding='utf8', errors='ignore') as f:
            content = f.read()
            return content

    def getContent(self):
        log.debug('loading ARCLI documents from JSON/filesystem: [%s]' % (self.filename))
        arCliFileContent = self._readContent(self.filename)
        arCliDefs = jstyleson.loads(arCliFileContent)
        allDocumentDefs = arCliDefs['arcliDocuments']
        loadedLabeledDocumentDefs = {}
        for k in allDocumentDefs.keys():
            log.debug('[%s]: processing: [%s]' % (self.filename, k))
            path = allDocumentDefs[k].get('path', None)
            if path is None:
                # Content is inline
                log.debug('[%s]: inline: [%s]' % (self.filename, k))
                continue
            # Content is elsewhere
            log.debug('[%s]: external: [%s] path: [%s]' % (self.filename, k, path))
            documentCount = 0
            loadedLabeledDocumentDefs[k] = {}
            for root, _, files in os.walk(os.path.join(self.basepath, path)):
                for name in files:
                    if not name.endswith(".json"):
                        continue
                    content = self._readContent(os.path.join(root, name))
                    log.debug('[%s]: external: [%s] loading file: [%s]' % (self.filename, k, name))
                    _arCliDefs = jstyleson.loads(content)
                    for command in _arCliDefs:
                        if command in loadedLabeledDocumentDefs[k]:
                            # Duplicate
                            log.error('[%s]: external: [%s] file: [%s] command: [%s] dropping duplicate' % (self.filename, k, name, command))
                            continue
                        log.debug('[%s]: external: [%s] file: [%s] command: [%s]' % (self.filename, k, name, command))
                        loadedLabeledDocumentDefs[k][command] = _arCliDefs[command]
                        documentCount += 1
            log.debug('[%s]: done: [%s] loaded %d documents' % (self.filename, k, documentCount))
        arCliDefs.update(loadedLabeledDocumentDefs)
        content = jstyleson.dumps(arCliDefs)
        #log.debug("loaded content: [%s]" % (content))
        return content


#
# Reads from a ZIP file
# Expects following file-system structure in ZIP file:
#
# arcli/
#   arcli.json
#   <class>/
#     <qualifier>/
#       <JSON file with document definition(s)
#       ...
#
# where <class> is one of ACX, AOS, ASW, COMWARE, IAP
# <class>/<qualifier> is the "label", i.e. AOS/default
#
class ArCliZipfileContentProvider(ContentProvider):
    def __init__(self, filename):
        self.filename = filename
        self.basepath = os.path.dirname(filename)

    def __str__(self):
        return "file://" + self.filename

    def _readContent(self, z, filename):
        with z.open(filename) as f:
            content = f.read().decode('utf-8')
            return content

    def getContent(self):
        log.debug('loading ARCLI documents from ZIP: [%s]' % (self.filename))
        with zipfile.ZipFile(self.filename) as z:
            arCliFileContent = self._readContent(z, 'arcli/arcli.json')
            arCliDefs = jstyleson.loads(arCliFileContent)
            allDocumentDefs = arCliDefs['arcliDocuments']
            loadedLabeledDocumentDefs = {}
            zipNamelist = z.namelist()
            for k in allDocumentDefs.keys():
                log.debug('[%s]: processing: [%s]' % (self.filename, k))
                path = allDocumentDefs[k].get('path', None)
                if path is None:
                    # Content is inline
                    log.debug('[%s]: inline: [%s]' % (self.filename, k))
                    continue
                # Content is elsewhere
                log.debug('[%s]: external: [%s] path: [%s]' % (self.filename, k, path))
                documentCount = 0
                loadedLabeledDocumentDefs[k] = {}
                for name in zipNamelist:
                    if not name.endswith(".json"):
                        continue
                    if not allDocumentDefs[k]['label'] in name:
                        continue
                    content = self._readContent(z, name)
                    log.debug('[%s]: external: [%s] loading file: [%s]' % (self.filename, k, name))
                    _arCliDefs = jstyleson.loads(content)
                    for command in _arCliDefs:
                        if command in loadedLabeledDocumentDefs[k]:
                            # Duplicate
                            log.error('[%s]: external: [%s] file: [%s] command: [%s] dropping duplicate' % (self.filename, k, name, command))
                            continue
                        log.debug('[%s]: external: [%s] file: [%s] command: [%s]' % (self.filename, k, name, command))
                        loadedLabeledDocumentDefs[k][command] = _arCliDefs[command]
                        documentCount += 1
                log.debug('[%s]: done: [%s] loaded %d documents' % (self.filename, k, documentCount))
            arCliDefs.update(loadedLabeledDocumentDefs)
            content = jstyleson.dumps(arCliDefs)
            #log.debug("loaded content: [%s]" % (content))
            return content


#
# Reads from following formats:
# - ZIP file (filename ends with .zip)
# - all-in-one JSON file (filename ends with .json)
# - file-system JSON files (filename ends with .json and additional path references exist in JSON file)
#
class ArCliContentProvider(ContentProvider):
    def __init__(self, filename):
        if filename.endswith(".zip"):
            self.contentProvider = ArCliZipfileContentProvider(filename)
        elif filename.endswith(".json"):
            self.contentProvider = ArCliFilesystemContentProvider(filename)
        else:
            raise Exception("ARCLI file must be JSON or ZIP")

    def __str__(self):
        return self.contentProvider.__str__()

    def getContent(self):
        return self.contentProvider.getContent()
