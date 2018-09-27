#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Curso de Elementos de Sistemas
# Desenvolvido por: Rafael Corsi <rafael.corsi@insper.edu.br>
#
# Data de criação: 11/2017
#
# Resumo: executa simulação da CPU via modelsim

import os
import shutil
import argparse
import fileinput
import time
import platform

from log import logError, logSim

# config file
CONFIG_FILE = "config.txt"

# TST DIR files
TST_DIR = "tst/"

# RAM files
RAM_INIT_FILE     = "_in.mif"
RAM_END_FILE      = "_tst.mif"
RAM_END_SIMU_FILE = "_end.mif"
OUT_SIM_LST = ""

# Path to vsim  #
PATH_VSIM =  os.path.join(os.environ.get('VUNIT_MODELSIM_PATH'), "vsim")

# Files used on this simulation
PATH_WORK       = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "Z01-Simulator-rtl")

END = "\n"


def setRuntimeDo(time, doFile):
        for line in fileinput.input(doFile, inplace = 1):
            if "run" in line:
                print("run "+str(time)+" ns")
            else:
                print(line.rstrip())


def rmFile(f):
    try:
        os.remove(f)
    except OSError:
        pass


# Recebe como parametro um diretorio do tipo teste
# e um caminho para o arquivo de programa (.mif)
# e executa as simulações contidas no arquivo de
# configuracao.
def simulateFromTestDir(testDir, hackDir, gui, verbose, rtlDir=PATH_WORK):

    #
    configFile = testDir+CONFIG_FILE

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile) + "/"

    os.path.abspath(hackDir)
    os.path.abspath(configFile)

    # file
    f = ""

    # Verificando se é diretorio
    if not os.path.exists(configFile):
        logError("Favor passar como parametro um diretorio do tipo test")
        return(1)

    # verifica se exist arquivo de config
    try:
        f = open(configFile, 'r')
    except:
        logError("Arquivo {} não encontrado".format(CONFIG_FILE))
        return(1)

    for l in f:
        if len(l.strip()):
            if (l.strip()[0] != '#'):
                # pega parametros e atribui caminhos globais
                # par[0] : Nome do teste (subpasta)
                # par[1] : quantidade de testes a serem executados
                # par[2] : tempo de simulação em ns
                par = l.rstrip().split();
                # nome do arquivo
                name = par[0]
                # tempo total de simulacao
                sTime = int(par[2])
                # paths
                mif = hackDir+name+".mif"
                # verifica se arquivo existe
                if os.path.isfile(mif):
                    # simulate
                    for i in range(0, int(par[1])):
                            # usar join ?
                            ramIn = pwd+TST_DIR+name+"/"+name+"{}".format(i) + RAM_INIT_FILE
                            ramOut = pwd+TST_DIR+name+"/"+name+str(i) + RAM_END_SIMU_FILE
                            print("Simulating " + os.path.relpath(mif) + " teste : " + str(i))
                            if os.path.isfile(ramIn):
                                    tic = time.time()
                                    if verbose is True :
                                        print(ramIn)
                                        print(mif)
                                        print(ramOut)
                                    simulateCPU(ramIn, mif, ramOut, sTime, gui, verbose, rtlDir=rtlDir)
                                    toc = time.time()
                                    print(" ({0:.2f} seconds)".format(toc-tic))
                            else:
                                    logError("Arquivo de simulacao não encontrado :")
                                    logError("                - {}".format(ramIn))
                                    return(-1)
                else:
                    logError("Arquivo hack não encontrado :")
                    logError("                - {}".format(mif))
                    return(-1)
    return(0)


def simulateCPU(ramIn, romIn, ramOut, time, debug, verbose, rtlDir=PATH_WORK):
    global OUT_SIM_LST
    rtlDir = os.path.abspath(rtlDir)

    PATH_DO         = os.path.join(rtlDir, "do", "sim.do")
    TEMP_IN_RAM_MIF = os.path.join(rtlDir, "tmpRAM.mif")
    TEMP_IN_ROM_MIF = os.path.join(rtlDir, "tmpROM.mif")
    OUT_RAM_MEM     = os.path.join(rtlDir, "out", "RAM.mem")
    OUT_ROM_MEM     = os.path.join(rtlDir, "out", "ROM.mem")
    # tosco, melhorar isso ! não pode ser global !
    # mas o gui simulator usa, colocar como parametro ?
    # ou criar uma classe
    OUT_SIM_LST     = os.path.join(rtlDir, "out", "SIM.lst")

    ramIn = os.path.abspath(ramIn)
    romIn = os.path.abspath(romIn)
    ramOut = os.path.abspath(ramOut)

   # try:
   #         os.remove(OUT_RAM_MEM)
   #         os.remove(OUT_ROM_MEM)
   #         os.remove(OUT_SIM_LST)
   #         print("removido")
   # except:
   #         print("simulateCPU: Falha em remove arquivos")
   #         pass

   # return(0)

    try:
        shutil.copyfile(ramIn, TEMP_IN_RAM_MIF)
        shutil.copyfile(romIn, TEMP_IN_ROM_MIF)
    except:
        logError("Arquivos não encontrados :")
        logError("    - {}".format(romIn))
        logError("    - {}".format(ramIn))
        return(1)

    if PATH_VSIM is None:
            logError("Configurar a variavel de ambiente : 'VUNIT_MODELSIM_PATH' ")
            return(1)

    setRuntimeDo(time, PATH_DO)

    v = ""

    if platform.system() == "Windows":
        if verbose is False:
            v = " > NUL "
    else:
        if verbose is False:
            v = " > /dev/null "

    c = ""
    if debug is False:
            c = " -c "

    # executa simulacao no modelsim
    owd = os.getcwd()
    os.chdir(rtlDir)

    os.system(PATH_VSIM  + c + " -do " + PATH_DO + v)
    os.chdir(owd)

    shutil.copyfile(OUT_RAM_MEM, ramOut)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-R", "--in_ram_mif", required=True, help="estado inicial da RAM no formato .mif ")
    ap.add_argument("-P", "--in_rom_mif", required=True, help="estado inicial da ROM no formato .mif ")
    ap.add_argument("-O", "--out_ram", required=True, help="diretorio para saída das simulacoes")
    ap.add_argument("-T", "--time_ns", required=True, help="Tempo em ns da simulacao")
    ap.add_argument("-d", "--debug", required=False,  action='store_true', help="open modelsim window")
    ap.add_argument("-v", "--verbose", required=False,  action='store_true', help="shows modelsim output")
    args = vars(ap.parse_args())

    if args["debug"]:
            debug = True
    else:
            debug = False

    if args["verbose"]:
            verbose = True
    else:
            verbose = False

    simulateCPU(ramIn=args["in_ram_mif"],
                romIn=args["in_rom_mif"],
                ramOut=args["out_ram"],
                time=args["time_ns"],
                debug=debug,
                verbose=verbose)
