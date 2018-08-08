# Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
#

from termcolor import colored

cLogiComb  = 'cyan'
cAssembly  = 'blue'
cAssembler = 'magenta'
cSimulation= 'green'
cTest      = 'yellow'
cError     = 'red'

def logLogiComb(s):
        print(colored(s,cLogiComb))

def logAssembly(s):
        print(colored(s,cAssembly))

def logAssembler(s):
        print(colored(s,cAssembler))

def logSim(s):
    print(colored(s,cSimulation))

def logTest(s):
    print(colored(s,cTest))

def logError(s):
    print(colored(s,cError))

