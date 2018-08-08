# -*- coding: utf-8 -*-
# Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
#
# script para gerar hack a partir de nasm
# suporta como entrada um único arquivo
# ou um diretório
# Possibilita também a geração do .mif

import os,sys
import argparse
from termcolor import colored
import time

TOOLSPATH = os.path.dirname(os.path.abspath(__file__))+"/../"

from simulateCPU import simulateCPU
from log import logError, logTest, logSim

# config file
CONFIG_FILE = "config.txt"

# TST DIR files
TST_DIR = "tst/"

# RAM files
RAM_INIT_FILE     = "_in.mif"
RAM_END_FILE      = "_tst.mif"
RAM_END_SIMU_FILE = "_end.mif"


# Abre arquivo de configuração a partir de
# um diretorio do tipo teste
def openConfigFile(testDir):

    configFile = testDir+CONFIG_FILE

    os.path.abspath(configFile)

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile)+"/"

    # file
    f = ""

    # Verificando se é diretorio
    if not os.path.exists(configFile):
        logError("Favor passar como parametro um diretorio do tipo test")
        return()

    # verifica se exist arquivo de config
    try:
        f = open(configFile, 'r')
        return(f)
    except:
        logError("Arquivo config.txt não encontrado")
        return(False)


# Compara dois arquivos RAM em busca
# de diferencas. Só verifica os endereços
# especificados em ramEnd
def compareRam(name, ramEnd, ramEndSimulation):
    # file
    fS = ""
    fE = ""

    # list
    ram = {}
    validacao = {}

    print("Starting  {} ....".format(name))

    # verifica se existe arquivos
    try:
        fS = open(ramEndSimulation, 'r')
    except:
        logError("Arquivo {} não encontrado".format(ramEndSimulation))
        return(False)

    # verifica se existe arquivos
    try:
        fE = open(ramEnd, 'r')
    except:
        logError("Arquivo {} não encontrado".format(ramEnd))
        return(False)

    # cria um vetor a partir do esperado da memória (.mif)
    for linha in fE:
        if linha.find(":") > 0:
                alocacao = linha.split(":")
                ram[int(alocacao[0].strip())] = alocacao[1].strip().replace(';','')

    # cria um vetor a partir do resultado da simulação
    for l in fS:
        if l.find(":") > 0:
                alocacao = l.split(":")
                validacao[int(alocacao[0].strip())] = alocacao[1].strip()

    # compara as memórias criadas buscando por diferencas
    for e, v in ram.items():
            if(ram[e] != validacao[e]):
                    print(colored("faill", 'red') + "    {}".format(name))
                    print("    endereco RAM : {}".format(e))
                    print("        esperado : " + ram[e])
                    print("          obtido : " + validacao[e])
                    return(False)
    print(colored("pass",'green') + "    {}".format(name))
    return(True)


# Recebe como parametro um diretorio do tipo teste
# e faz a comparação de todos os testes especificados
# no arquivo de configuração
def compareFromTestDir(testDir):

    # caminho do arquivo de configuracao
    configFile = testDir+CONFIG_FILE
    pwd = os.path.dirname(configFile)+"/"
    testeResults = []

    f = openConfigFile(testDir)

    if f is not False:
        for l in f:
            if l.strip()[0]!='#':
                par   = l.rstrip().split();
                name  = par[0]
                nTest = int(par[1])
                for i in range (0, nTest):
                        nameTest   = name + str(i)
                        ramEnd     = pwd + "/tst/" + name + "/" + name + "{}".format(i) + RAM_END_FILE
                        ramEndSimu = pwd + "/tst/" + name + "/" + nameTest + RAM_END_SIMU_FILE
                        if(os.path.isfile(ramEnd) and os.path.isfile(ramEndSimu)):
                            result = {'nome':name, 'resultado':compareRam(nameTest, ramEnd, ramEndSimu), 'teste':i}
                            testeResults.append(result)
    print("==== Summary ===================================")
    for result in testeResults:
        if result['resultado']:
            print(colored("pass",'green') + "    {} teste: {}".format(result['nome'], result['teste']))
        else:
            print(colored("fail",'red') + "    {} teste {}".format(result['nome'], result['teste']))

