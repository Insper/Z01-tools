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
import re

TOOLSPATH = os.path.dirname(os.path.abspath(__file__))+"/../"

from toMIF import toMIF
from log import logError, logAssembler

jar = TOOLSPATH+"jar/Z01-Assembler.jar"

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

def assembler(jar, nasm, hack, mif):

    error = 0
    log = []

    pwd = os.path.dirname(os.path.abspath(__file__))

    # global path
    os.path.abspath(nasm)
    os.path.abspath(hack)

    if not os.path.exists(os.path.dirname(hack)):
        os.makedirs(os.path.dirname(hack))

    if(os.path.isdir(nasm)) :
        if(os.path.isdir(hack)) :
            for filename in os.listdir(nasm):
                if filename.endswith("nasm"):
                    #logAssembler(" > "+filename)
                    nHack = hack+filename[:-5]+".hack"
                    nMif  = hack+filename[:-5]+".mif"
                    nNasm = nasm+filename
                    if not os.path.basename(nNasm).startswith('.'):
                        print("Compiling {} to {}".format(os.path.basename(nNasm), os.path.basename(nHack)))
                        if callJava(jar, nNasm, nHack) is not 0:
                            status = 'true'
                            error  = -1
                        if mif:
                            status = 'false'
                            toMIF(nHack, nMif)
                        log.append({'name': filename, 'status': status})
            return(error, log)
        else:
            logError("output must be folder for folder input!")
            return(-1)
    else:
        hack = hack+".hack"
        callJava(jar, nasm, hack)
        if(mif):
            toMIF(hack, os.path.splitext(hack)[0]+".mif")
    return(0)


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
