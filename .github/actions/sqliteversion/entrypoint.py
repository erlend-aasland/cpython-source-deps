#!/usr/bin/env python3.9

import itertools
import urllib.request
from html.parser import HTMLParser

URL = "https://sqlite.org/chronology.html"
row_counter = itertools.count()
rows = {}


def get_chronology_page():
    """Fetch history of SQLite releases"""
    with urllib.request.urlopen(URL) as f:
        return f.read().decode()


class ParseVersionTable(HTMLParser):
    def _add_row(self):
        self.current_row = next(row_counter)
        self.column_counter = itertools.count()
        rows[self.current_row] = {}

    def _add_column(self, attrs):
        self.current_column = next(self.column_counter)
        rows[self.current_row][self.current_column] = self._get_version_attr(attrs)

    def _add_data(self, data):
        try:
            if not rows[self.current_row][self.current_column]:
                rows[self.current_row][self.current_column] = data
        except AttributeError:
            pass

    def _get_version_attr(self, attrs):
        VERSION_ATTR = "data-sortkey"
        for attr in attrs:
            if attr[0] == VERSION_ATTR:
                return attr[1]

    def _verify_row(self):
        row = rows[self.current_row]
        assert len(row) == 2

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._add_row()
        elif tag == "td":
            self._add_column(attrs)

    def handle_endtag(self, tag):
        if tag == "tr":
            self._verify_row()

    def handle_data(self, data):
        self._add_data(data)


if __name__ == "__main__":
    parser = ParseVersionTable()
    parser.feed(get_chronology_page())

    rows = [(v[1], v[0]) for k, v in rows.items() if v]
    latest = rows[0]

    print(f"::set-output name=version::{latest[0]}")
    print(f"::set-output name=date::{latest[1]}")
