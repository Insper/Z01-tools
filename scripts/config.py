from os.path import join, dirname
import sys, os, shutil, subprocess
import argparse


ROOT_PATH = subprocess.Popen(
    ['git', 'rev-parse', '--show-toplevel'],
    stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
PROJ_PATH = os.path.join(ROOT_PATH, 'Projetos')
TOOL_PATH = os.path.join(ROOT_PATH, 'Projetos', 'Z01-tools')
TOOL_SCRIPT_PATH = os.path.join(TOOL_PATH, 'scripts')
PATH_SIMULATOR = os.path.join(TOOL_PATH, 'Z01-Simulator-rtl')

# Path to vsim  #
PATH_VSIM =  os.path.join(os.environ.get('VUNIT_MODELSIM_PATH'), "vsim")

PROJ_C_PATH = os.path.join(PROJ_PATH, 'C-LogicaCombinacional')
PROJ_D_PATH = os.path.join(PROJ_PATH, 'D-UnidadeLogicaAritmetica')
PROJ_E_PATH = os.path.join(PROJ_PATH, 'E-LogicaSequencial')
PROJ_F_PATH = os.path.join(PROJ_PATH, 'F-Assembly')
PROJ_G_PATH = os.path.join(PROJ_PATH, 'G-Computador')
PROJ_H_PATH = os.path.join(PROJ_PATH, 'H-Assembler')
PROJ_I_PATH = os.path.join(PROJ_PATH, 'I-VM')
PROJ_J_PATH = os.path.join(PROJ_PATH, 'J-VMTranslator')

Z01_GUI_PATH = TOOL_PATH+'/Z01-Simulator-GUI/'

PROJ_C_NAME = 'Logica Combinacional'
PROJ_D_NAME = 'Unidade Logica Aritmetica'
PROJ_E_NAME = 'Logica Sequencial'
PROJ_F_NAME = 'Assembly'
PROJ_G_NAME = 'Computador'
PROJ_H_NAME = 'Assembler'
PROJ_I_NAME = 'VM'
PROJ_J_NAME = 'VMTranslator'

sys.path.insert(0,PROJ_C_PATH)
sys.path.insert(0,PROJ_D_PATH)
sys.path.insert(0,PROJ_E_PATH)
sys.path.insert(0,PROJ_F_PATH)
sys.path.insert(0,PROJ_G_PATH)
sys.path.insert(0,PROJ_H_PATH)
sys.path.insert(0,PROJ_I_PATH)
sys.path.insert(0,PROJ_J_PATH)

# config file
CONFIG_FILE = "config.txt"

# TST DIR files
TST_DIR = "tst/"

# RAM files
RAM_INIT_FILE     = "_in.mif"
RAM_END_FILE      = "_tst.mif"
RAM_END_SIMU_FILE = "_end.mif"
OUT_SIM_LST = ""

END = "\n"

ASSEMBLER_JAR = TOOL_PATH+"/jar/Z01-Assembler.jar"

from report import report
from notificacao import notificacao
from testeVHDL import vhdlScript

from testeLogicaCombinacional import tstLogiComb
#from testeULA import tstUla
#from testeLogicaSequencial import tstLogiSeq

#from toMIF import toMIF
#from testeAssembly import compareRam, compareFromTestDir
#from simulateCPU import simulateFromTestDir

ERRO_NONE = 0
ERRO_ASSEMBLER = 1
ERRO_ASSEMBLER_FILE = 2
ERRO_SIMULATION = 3
ERRO_SIMULATION_TESTE = 4
ERRO_VHDL = 5
ERRO_VHDL_TESTE = 6
