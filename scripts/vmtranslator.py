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
import subprocess
from log import logError
from config import *

TOOLSPATH = os.path.dirname(os.path.abspath(__file__))+"/../"

jarD = TOOLSPATH+"jar/Z01-VMTranslator.jar"

def callJava(jar, vm, nasm, bootstrap=False):
    command = "java -jar " + jar + " " + vm + " -o " + nasm
    if not bootstrap:
        command += " -n"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    err = proc.wait()
    return(err)


def vmtranslator(bootstrap, vm, nasm, jar=jarD):

    pwd = os.path.dirname(os.path.abspath(__file__))

    # verifica se existe destino
    if not os.path.exists(os.path.dirname(nasm)):
        os.makedirs(os.path.dirname(nasm))

    # verifica se é diretorio
    if(os.path.isdir(vm)):
        if(os.path.isdir(nasm)):
            for filename in os.listdir(vm):
                if(os.path.isdir(vm+'/'+filename)):
                    nNasm = nasm+filename+".nasm"
                else:
                    nNasm = nasm+filename[:-3]+".nasm"
                nVM = vm+filename
                if not os.path.basename(nVM).startswith('.'):
                    print("Compiling {} to {}".format(os.path.basename(nVM), os.path.basename(nNasm)))
                    rtn = callJava(jar, nVM, nNasm, bootstrap)
                    if(rtn > 0):
                        return(rtn)
        else:
            logError("output must be folder for folder input!")
    # é arquivo
    else:
        nNasm = nasm+".nasm"
        rtn = callJava(vm, nNasm, jar)
        return(rtn)

def vmtranslatorFromTestDir(jar, testDir, vmDir, nasmDir, bootstrap=False):

    error = 0
    log = []

    configFile = testDir+CONFIG_FILE

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile) + "/"

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

    print(" 1/2 Removendo arquivos .nasm" )
    print("  - {}".format(nasmDir))
    for item in nasmDir:
        if item.endswith(".nasm"):
            os.remove(os.path.join(dir_name, item))

    print(" 2/2 Gerando arquivos   .nasm")
    print("  - {}".format(vmDir))

    for l in f:
        if len(l.strip()):
            if (l.strip()[0] != '#'):

                # pega parametros e atribui caminhos globais
                # par[0] : Nome do teste (subpasta)
                # par[1] : quantidade de testes a serem executados
                # par[2] : tempo de simulação em ns
                par = l.rstrip().split();
                name = par[0]
                vm = vmDir+name
                nasm = nasmDir+name+'.nasm'
                nasm = nasm.replace('vm/', '')
                nasm = nasm.replace('vmExamples/', '')
                print("  - " +  vm)
                print("  ->" +nasm)
                e = callJava(jar, vm, nasm, bootstrap)
                if e > 0:
                    return ERRO_ASSEMBLER, log
    return ERRO_NONE, log



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
    vmtranslator(nasm=args["nasm"], hack=args["hack"], mif=mif)
