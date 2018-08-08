# -*- coding: utf-8 -*-
# Eduardo Marossi & Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas

import shutil
from PyQt5.QtGui import QStandardItem

def stream_to_file(fsrc, filename):
   fsrc.seek(0, 0)
   fdest = open(filename, "w", newline="\n")
   for i, l in enumerate(fsrc):
      fdest.write(l)
   fsrc.seek(0, 0)
   return filename


def file_to_stream(filename, fdest):
   fdest.seek(0, 0)
   fsrc = open(filename, "r")
   shutil.copyfileobj(fsrc, fdest)
   fsrc.close()
   return fdest


def create_empty_rom(file_dest, size=1024):
   dest = open(file_dest, "w")
   for i in range(0, size):
        dest.write("0000000000000000\n")
   dest.close()
   return file_dest


def copy_file_to_model(file_in, model, preprocessor=None):
   file_in.seek(0, 0)
   for i, l in enumerate(file_in):
      data = l
      if preprocessor is not None:
         data = preprocessor(data)
      model.setItem(i, QStandardItem(data))


def copy_model_to_file(model, f, preprocessor=None):
   f.seek(0, 0)
   for i in range(0, model.rowCount()):
      index = model.index(i, 0)
      data = model.itemFromIndex(index).text().strip()
      if preprocessor is not None:
         data = preprocessor(data)
      f.write(data + "\n")
   f.seek(0, 0)
   return f

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def copy_file_to_file(f1, f2, preprocessor=None):
    f1.seek(0, 0)
    f2.seek(0, 0)
    for i, l in enumerate(f1):
        data = l
        if preprocessor is not None:
            data = preprocessor(data)
        f2.write(data)
    f2.seek(0, 0)
    f1.seek(0, 0)
    return f2