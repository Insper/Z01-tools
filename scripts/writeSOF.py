# Rafael Corsi @ insper.edu.br
# /2018
# Disciplina Elementos de Sistemas
#
# Abril/2018

import os
import argparse
import subprocess

def writeSOF(cdf):
    # verifica se o .mif existe
    cdf = os.path.abspath(cdf)

    if not os.path.isfile(cdf):
        print("Arquivo {} não encontrado".format(cdf))
        return(1)

    print("Programando FPGA ...")
    pPGM = subprocess.Popen("quartus_pgm -c 1 -m jtag " + cdf, shell=True)

    exit_codes = pPGM.wait()

    print("end")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--cdf" , required=True, help="arquivo de configuracao do gravador do quartus - .cdf")
    args = vars(ap.parse_args())
    root = os.getcwd()
    writeSOF(cdf=args["cdf"])
