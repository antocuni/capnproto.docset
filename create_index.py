#!/usr/bin/env python

import os
from textwrap import dedent
import sqlite3
import py

ROOT = py.path.local(__file__).dirpath()
DOCSET = ROOT.listdir('*.docset')[0]
DOCUMENTS = DOCSET.join('Contents', 'Resources', 'Documents')
INDEX = DOCSET.join('Contents', 'Resources').ensure(dir=True).join('docSet.dsidx')

class IndexDb(object):

    def __init__(self, path):
        self.path = path
        if path.check():
            path.remove()
        self.db = sqlite3.connect(str(path))
        self.cur = self.db.cursor()

        self.cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        self.cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    def add(self, name, type, path):
        print '[%s]: %s' % (type, name)
        self.cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, type, path))

    def scan_html(self, path):
        from lxml import etree
        target = path.relto(DOCUMENTS)
        with path.open() as f:
            tree = etree.parse(f, etree.HTMLParser())
        title = tree.find('head/title').text
        title = title.replace("Cap'n Proto: ", "")
        self.add(title, 'Guide', target)
        #
        headers = tree.findall('.//h2') + tree.findall('.//h3')
        for h in headers:
            link = '%s#%s' % (target, h.attrib['id'])
            self.add(h.text, 'Section', link)

    def close(self):
        self.db.commit()
        self.db.close()

def main():
    db = IndexDb(INDEX)
    for htmlpath in DOCUMENTS.visit('*.html'):
        if htmlpath.basename in ('index.html', 'index-2.html', 'tw_profile.html'):
            continue
        db.scan_html(htmlpath)
    db.close()
    

if __name__ == '__main__':
    main()
