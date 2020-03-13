#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Curso de Elementos de Sistemas
# Desenvolvido por: Rafael Corsi <rafael.corsi@insper.edu.br>
#
# Data de criação: 11/2017
#
# Resumo: executa simulação da CPU via modelsim

import os, shutil, argparse
import fileinput, time, platform
from log import logError, logSim
import config
import util
from genImg import lcdToimg

def setRuntimeDo(time, doFile):
        for line in fileinput.input(doFile, inplace = 1):
            if "run" in line:
                print("run "+str(time)+" ns")
            else:
                print(line.rstrip())


def simulateFromTestDir(testDir, hackDir, gui, verbose, nasmFile=None,rtlDir=config.PATH_SIMULATOR):

    error = 0
    log = []

    configFile = testDir+config.CONFIG_FILE

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile) + "/"

    f = util.openConfigFile(testDir)
    for l in f:
        if len(l.strip()):
            if ((l.strip()[0] != '#') and ( (l.strip().find('.nasm') > 0 ) or (l.strip().find('.vm') > 0) )):
                # pega parametros e atribui caminhos globais
                # par[0] : Nome do teste (subpasta)
                # par[1] : quantidade de testes a serem executados
                # par[2] : tempo de simulação em ns
                par = l.rstrip().split();
                if(l.strip().find('.vm') > 0):
                    name = par[0][:-3]
                else:
                    name = par[0][:-5]
                sTime = int(par[2])
                mif = hackDir+name+".mif"

                # verifica se é para executar compilar
                # apenas um arquivo da lista
                if nasmFile is not None:
                        if name != nasmFile:
                                continue

                # verifica se arquivo existe
                if os.path.isfile(mif):
                    # simulate
                    for i in range(0, int(par[1])):
                            # usar join ?
                            ramIn = pwd+config.TST_DIR+name+"/"+name+"{}".format(i) + config.RAM_INIT_FILE
                            ramOut = pwd+config.TST_DIR+name+"/"+name+str(i) + config.RAM_END_SIMU_FILE
                            lcdOut = pwd+config.TST_DIR+name+"/"+name+str(i) + config.LCD_PGM_FILE
                            print(os.path.relpath(mif) + " teste : " + str(i))

                            if os.path.isfile(ramIn):
                                    tic = time.time()
                                    if verbose is True :
                                        print(ramIn)
                                        print(mif)
                                        print(ramOut)
                                    simulateCPU(ramIn, mif, ramOut, lcdOut, sTime, gui, verbose, rtlDir=rtlDir)
                                    toc = time.time()
                                    print(" ({0:.2f} seconds)".format(toc-tic))
                            else:
                                    logError("Arquivo de simulacao não encontrado :")
                                    logError("                - {}".format(ramIn))
                                    log.append({'name': name, 'status': 'Simulacao Arquivo Fail'})
                                    return -1, log
                else:
                    logError("Arquivo hack não encontrado :")
                    logError("                - {}".format(mif))
                    log.append({'name': mif, 'status': 'Simulacao Arquivo Fail'})
                    return -1, log
    return 0, log


def simulateCPU(ramIn, romIn, ramOut, lcdOut, time, debug, verbose, rtlDir=config.PATH_SIMULATOR):
    global OUT_SIM_LST
    rtlDir = os.path.abspath(rtlDir)

    PATH_DO         = os.path.join(rtlDir, "do", "sim.do")
    TEMP_IN_RAM_MIF = os.path.join(rtlDir, "tmpRAM.mif")
    TEMP_IN_ROM_MIF = os.path.join(rtlDir, "tmpROM.mif")
    OUT_RAM_MEM     = os.path.join(rtlDir, "out", "RAM.mem")
    OUT_ROM_MEM     = os.path.join(rtlDir, "out", "ROM.mem")
    OUT_LCD_MEM     = os.path.join(rtlDir, "out", "LCD.mem")
    # tosco, melhorar isso ! não pode ser global !
    # mas o gui simulator usa, colocar como parametro ?
    # ou criar uma classe
    OUT_SIM_LST     = os.path.join(rtlDir, "out", "SIM.lst")

    ramIn = os.path.abspath(ramIn)
    romIn = os.path.abspath(romIn)
    ramOut = os.path.abspath(ramOut)
    lcdOut = os.path.abspath(lcdOut)

    try:
        shutil.copyfile(ramIn, TEMP_IN_RAM_MIF)
        shutil.copyfile(romIn, TEMP_IN_ROM_MIF)
    except:
        logError("Arquivos não encontrados :")
        logError("    - {}".format(romIn))
        logError("    - {}".format(ramIn))
        return(1)

    if config.PATH_VSIM is None:
            logError("Configurar a variavel de ambiente : 'VUNIT_MODELSIM_PATH' ")
            return(1)

    setRuntimeDo(time, PATH_DO)

    v = ""

    if verbose is False:
        v = " > /dev/null "

    c = ""
    if debug is False:
            c = " -c "

    # executa simulacao no modelsim
    owd = os.getcwd()
    os.chdir(rtlDir)

    os.system(config.PATH_VSIM  + c + " -do " + PATH_DO + v)
    os.chdir(owd)

    try:
        shutil.copyfile(OUT_RAM_MEM, ramOut)
    except:
        logError("Falha na simulação")
        return(1)

    lcd = lcdToimg(OUT_LCD_MEM, lcdOut)
