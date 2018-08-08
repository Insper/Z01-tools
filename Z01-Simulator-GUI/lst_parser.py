# -*- coding: utf-8 -*-
# Eduardo Marossi & Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas

import argparse
import sys

class LSTParser:
    def __init__(self, file_in):
        self.file_in = file_in
        self.file_in.seek(0, 2)
        self.file_size = self.file_in.tell();
        self.file_in.seek(0, 0)
        self.headers = None
        self.go_begin()

    def fix_line(self, line):
        while line.find("  ") != -1:
            line = line.replace("  ", " ")
        return line.strip()

    def go_begin(self):
        self.file_in.seek(0, 0)
        if not self.has_more():
            return
        self.headers = self._read_next()

    def _read_next(self):
        return self.fix_line(self.file_in.readline()).split(" ")

    def advance(self):
        results = {}
        data = self._read_next()
        for i in range(0, len(data)):
            caption = self.headers[i]
            results[caption] = data[i]
        return results

    def has_more(self):
        return self.file_in.tell() != self.file_size

    def close(self):
        self.file_in.close()

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("file_in",  help="LST file")
    args = argp.parse_args()
    file_in  = open(args.file_in, "r")
    app  = LSTParser(file_in)
    while app.has_more():
        print(app.advance())
    sys.exit(0)

