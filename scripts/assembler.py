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
from config import *
from toMIF import toMIF
from log import logError, logAssembler

jar = TOOL_PATH+"jar/Z01-Assembler.jar"

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

def assemblerFromTestDir(jar, testDir, nasmDir, hackDir):

    print("-------------------------")
    print("- Montando arquivos      ")
    print("-------------------------")

    error = 0
    log = []

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

    print(" 1/2 Removendo arquivos .hack" )
    print("  - {}".format(hackDir))
    clearbin(hackDir)

    print(" 2/2 Gerando arquivos   .hack")
    print("  - {}".format(nasmDir))

    for l in f:
        if len(l.strip()):
            if (l.strip()[0] != '#'):
                # pega parametros e atribui caminhos globais
                # par[0] : Nome do teste (subpasta)
                # par[1] : quantidade de testes a serem executados
                # par[2] : tempo de simulação em ns
                par = l.rstrip().split();
                name = par[0]
                nasm = nasmDir+name+".nasm"
                hack = hackDir+name+'.hack'
                mif  = hackDir+name+".mif"

                if os.path.isfile(nasm):
                    e, l = assemblerFile(jar, nasm, hack, mif)
                    log.append(l)
                    if e > 0:
                        return ERRO_ASSEMBLER, log
                else:
                    logError("Arquivo nasm não encontrado :")
                    logError("                - {}".format(nasm))
                    log.append({'name': mif, 'status': 'false'})
                    return ERRO_ASSEMBLER_FILE, log
    return ERRO_NONE, log


def assemblerAll(jar, nasm, hack, mif):

    print("-------------------------")
    print("- Montando arquivos      ")
    print("-------------------------")

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
                if filename.endswith("nasm"):
                    #logAssembler(" > "+filename)
                    nHack = hack+filename[:-5]+".hack"
                    nMif  = hack+filename[:-5]+".mif"
                    nNasm = nasm+filename
                    if not os.path.basename(nNasm).startswith('.'):
                        e, l = assemblerFile(jar, nNasm, nHack, nMif)
                        log.append(l)
                        if e > 0:
                            return ERRO_ASSEMBLER, log
        else:
            logError("output must be folder for folder input!")
            return ERRO_ASSEMBLER_FILE, log
    return ERRO_NONE, log

def assemblerFile(jar, nasm, hack, mif):

    error = ERRO_NONE

    if not os.path.exists(os.path.dirname(hack)):
        os.makedirs(os.path.dirname(hack))

    hack = hack
    print("   - {} to {}".format(os.path.basename(nasm), os.path.basename(hack)))
    if callJava(jar, nasm, hack) is not 0:
        status = 'Assembler Fail'
        error  = 1
    else:
        status = 'Assembler Ok'
        error = 0
    if mif:
        toMIF(hack, os.path.splitext(hack)[0]+".mif")
    log = ({'name': os.path.basename(os.path.splitext(hack)[0]), 'status': status})

    return error, log


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--nasm" , required=True, help="arquivo nasm")
    ap.add_argument("-o", "--hack" , required=True, help="arquivo hack de saída")
    ap.add_argument("-m", "--mif" , help="gera o arquivo mif")
    args = vars(ap.parse_args())
    if(args["mif"]):
        mif = True
    else:
        mif = False
    root = os.getcwd()
    assembler(nasm=args["nasm"], hack=args["hack"], mif=mif)
