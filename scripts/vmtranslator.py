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
