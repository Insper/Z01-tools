#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Curso de Elementos de Sistemas
# Desenvolvido por: Renan Trevisoli <renantd@insper.edu.br>
#
# Adaptado de :     Rafael Corsi <rafael.corsi@insper.edu.br>
#                   Pedro Cunial   <pedrocc4@al.insper.edu.br>
#                   Luciano Soares <lpsoares@insper.edu.br>
# Data de criação: 07/2017

import os

import util
import glob
from termcolor import colored

class vhdlScript_cocotb(object):

    def __init__(self, path_in, path_tst, path_proj):
        self.path_in = path_in
        self.path_tst = path_tst
        self.path_proj = path_proj
        self.runned_test = []
        self.result = []
        self.results_file = 'results.xml'
        if not os.path.exists(self.path_tst +'/waves'):
	        os.makedirs(self.path_tst +'/waves')

    def runTstConfigFile(self, tst):
        try:
            f = util.openConfigFile(tst)
            if f is not False:
                for l in f:
                    ls = l.strip()
                    if ls and ('#' not in l):
                        if ls[-4:] == '.vhd':
                            self.runned_test.append(ls[:-4].lower()) 
                            code = os.system('(cd ' + self.path_tst + ' && ' + 'make TOPLEVEL=' + ls[:-4].lower() + ' TESTCASE=tb_' + ls[:-4] + ' SIM_ARGS=--vcd=waves/' + ls[:-4].lower() + '.vcd ' + self.results_file + ')')
                            if code == 0:   
                                if  self.read_xml() == 0:                                                       
                                    print("Teste " + ls[:-4] + ": " + colored('Passed', 'green'))
                                    self.result.append('Passed') 
                                else:
                                    print("Teste " + ls[:-4] + ": " + colored('Failed', 'red'))
                                    self.result.append('Failed')   
                            else:
                                print("Teste " + ls[:-4] + ": " + colored('Failed', 'red'))
                                self.result.append('Failed')       
                                      
            return(0)
        except:
            return(-1)


    def read_xml(self):
        file_in = open(self.path_tst + self.results_file,"r")
        Lines_in = file_in.readlines() 
        file_in.close()

        for s in Lines_in:
            if 'failure' in s:
                return(-1)
        return(0)

    def show_results(self):
        for i in range(len(self.runned_test)):
            if self.result[i] == 'Passed':
                print('{:25s}: '.format(self.runned_test[i]) + colored('Passed', 'green'))
            else:
                print('{:25s}: '.format(self.runned_test[i]) + colored('Failed', 'red'))
    
