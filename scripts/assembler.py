# -*- coding: utf-8 -*-
# Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
#
# script para gerar hack a partir de nasm
# suporta como entrada um único arquivo
# ou um diretório
# Possibilita também a geração do .mif

import os,sys,argparse, subprocess, re
import config
from toMIF import toMIF
from log import logError, logAssembler
from os.path import basename
from notificacao import notificacao


def compileAllNotify(error, log):
    noti = notificacao('Compile all')

    if not error:
        noti.ok('\n Bem sucedido')
        return(0)
    else:
        noti.error('\n Falhou: {}'.format(log[-1]['name']))
        return(-1)


def compileAll(jar, nasm, hack):
    i = 0; erro = 0;
    print(" 1/2 Removendo arquivos antigos .hack" )
    print("  - {}".format(hack))
    clearbin(hack)

    print(" 2/2 Gerando novos arquivos   .hack")
    for n in nasm:
        print("  - {}".format(n))
        e, l = assemblerAll(jar, n, hack, True)
        erro += e;
    return e, l


def callJava(jar, nasm, hack):
    command = "java -jar " + jar + " -i " + nasm + " -o " + hack
    proc = subprocess.Popen(command, shell=True)
    err = proc.wait()
    return(err)


def clearbin(hack):
    try:
        shutil.rmtree(hack)
    except:
        pass


def assemblerFromTestDir(jar, testDir, nasmDir, hackDir, nasmFile=None):

    error = 0
    log = []

    configFile = testDir+config.CONFIG_FILE

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile) + "/"

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

    print(" 1/2 Removendo arquivos .hack" )
    print("  - {}".format(hackDir))
    clearbin(hackDir)
    os.makedirs(os.path.dirname(hackDir), exist_ok=True)

    print(" 2/2 Gerando arquivos   .hack")
    print("  - {}".format(nasmDir))

    for l in f:
        if len(l.strip()):
            if (l.strip()[0] != '#'):
                if (l.strip().find('.nasm') > 0) or (l.strip().find('.vm') > 0):

                    # par[0] : Nome do teste (subpasta)
                    # par[1] : quantidade de testes a serem executados
                    # par[2] : tempo de simulação em ns
                    par = l.rstrip().split()
                    if(l.strip().find('.vm') > 0):
                        name = par[0][:-3]
                    else:
                        name = par[0][:-5]
                    hack = hackDir+name+'.hack'
                    mif  = hackDir+name+".mif"
                    found = False

                    if isinstance(nasmDir, list):
                        nasmDir = nasmDir
                    else:
                        nasmDir = [nasmDir, '']

                    for n in nasmDir:
                        nasm = n+name+".nasm"
                        # verifica se é para executar compilar
                        # apenas um arquivo da lista
                        if nasmFile is not None:
                            if name != nasmFile:
                                continue
                        if os.path.isfile(nasm):
                            e, l = assemblerFile(jar, nasm, hack, mif)
                            log.append(l)
                            if e > 0:
                                return config.ERRO_ASSEMBLER, log
                            found = True
                    if found is False:
                        logError("Arquivo nasm não encontrado :")
                        logError("                - {}".format(nasm))
                        log.append({'name': mif, 'status': 'false'})
                        return config.ERRO_ASSEMBLER_FILE, log
    return config.ERRO_NONE, log


def assemblerAll(jar, nasm, hack, mif):

    error = -1
    log = []

    pwd = os.path.dirname(os.path.abspath(__file__))

    # global path
    os.path.abspath(nasm)
    os.path.abspath(hack)

    if not os.path.exists(os.path.dirname(hack)):
        os.makedirs(os.path.dirname(hack))

    if(os.path.isdir(nasm)):
        if(os.path.isdir(hack)):
            for filename in os.listdir(nasm):
                status = 'true'
                if (filename.strip().find('.nasm') > 0):
                    nHack = hack+filename[:-5]+".hack"
                    nMif  = hack+filename[:-5]+".mif"
                    nNasm = nasm+filename
                    if not os.path.basename(nNasm).startswith('.'):
                        e, l = assemblerFile(jar, nNasm, nHack, nMif)
                        log.append(l)
                        if e > 0:
                            return config.ERRO_ASSEMBLER, log
        else:
            logError("output must be folder for folder input!")
            return config.ERRO_ASSEMBLER_FILE, log
    return config.ERRO_NONE, log


def assemblerFile(jar, nasm, hack, mif):
    error = config.ERRO_NONE

    if not os.path.exists(os.path.dirname(hack)):
        os.makedirs(os.path.dirname(hack))

    hack = hack
    print("   - {} to {}".format(os.path.basename(nasm), os.path.basename(hack)))
    if callJava(jar, nasm, hack) is not 0:
        status = 'Assembler Fail'
        error  = config.ERRO_ASSEMBLER
    else:
        status = 'Assembler Ok'
        error = config.ERRO_NONE
    if mif:
        toMIF(hack, os.path.splitext(hack)[0]+".mif")
    log = ({'name': os.path.basename(os.path.splitext(hack)[0]), 'status': status})

    return error, log
