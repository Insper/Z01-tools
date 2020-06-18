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

import config
import util

def callJava(jar, vm, nasm, bootstrap=False):

    command = "java -jar " + jar + " " + vm + " -o " + nasm
    if not bootstrap:
        command += " -n"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    err = proc.wait()
    return(err)


def vmtranslator(bootstrap, vmDir, nasm, jar=config.VMTRANSLATOR_JAR):

    if not os.path.exists(os.path.dirname(nasm)):
        os.makedirs(os.path.dirname(nasm))

    if not isinstance(vmDir, list):
        vmDir = [vmDir, '']

    for vm in vmDir:
        if(vm != ''):
            if(os.path.isdir(nasm)):
                for filename in os.listdir(vm):
                    print(filename)
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
        #else:
        #    
        #    import pdb; pdb.set_trace()
        #    nNasm = nasm+".nasm"
        #    rtn = callJava(jar, vm, nNasm)
        #    return(rtn)

def vmtranslatorFromTestDir(jar, testDir, vmDir, nasmDir, bootstrap=False):

    error = 0
    log = []

    configFile = testDir+config.CONFIG_FILE

    # caminho do arquivo de configuracao
    pwd = os.path.dirname(configFile) + "/"

    print(" 1/2 Removendo arquivos .nasm" )
    print("  - {}".format(nasmDir))
    for item in nasmDir:
        if item.endswith(".nasm"):
            os.remove(os.path.join(dir_name, item))

    print(" 2/2 Gerando arquivos   .nasm")
    print("  - {}".format(vmDir))

    f = util.openConfigFile(configFile)

    for l in f:
        if len(l.strip()):
            if (l.strip()[0] != '#'):
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
                    return config.ERRO_ASSEMBLER, log
    return config.ERRO_NONE, log
