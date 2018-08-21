#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Curso de Elementos de Sistemas
# Desenvolvido por: Rafael Corsi <rafael.corsi@insper.edu.br>
#
# Adaptado de :     Pedro Cunial   <pedrocc4@al.insper.edu.br>
#                   Luciano Soares <lpsoares@insper.edu.br>
# Data de criação: 07/2017

import os

# vnuit para vhdl
from vunit import VUnitCLI, VUnit
from log import logError

# config file
CONFIG_FILE = "config.txt"

# Abre arquivo de configuração a partir de
# um diretorio do tipo teste
def openConfigFile(testDir):

    configFile = testDir+CONFIG_FILE

    os.path.abspath(configFile)

    # file
    f = ""

    # Verificando se é diretorio
    if not os.path.exists(testDir):
        logError("Favor passar como parametro um diretorio do tipo test")
        return()

    # verifica se exist arquivo de config
    try:
        f = open(configFile, 'r')
        return(f)
    except:
        logError("Arquivo config.txt não encontrado")
        return(False)


class vhdlScript(object):

    def __init__(self, log):
        # config
        self.cli = VUnitCLI()
        self.args = self.cli.parse_args()
        self.args.num_threads = 4
        self.args.xunit_xml = log
        self.ui = VUnit.from_args(args=self.args)
        self.lib = self.ui.add_library("lib")

    def add_src_lib(self, path):
        for filename in os.listdir(path):
            if(filename.split(".")[-1] == "vhd"):
                if filename[0]  != '.':
                    self.lib.add_source_files(path+filename)

    def useLib(self, lib):
        self.lib = lib

    def addSrc(self, pwd):
        print("-----------------")
        print(pwd)
        print("-----------------")
        self.add_src_lib(pwd)

    def addTstConfigFile(self, tst):
        f = openConfigFile(tst)
        if f is not False:
            for l in f:
                if l.strip():
                    if '#' not in l:
                        self.addSrcFile(tst + "tst/tb_" + l[:-1])

    def addSrcFile(self, f):
        self.lib.add_source_files(f)

    def run(self):
        self.ui.main()
