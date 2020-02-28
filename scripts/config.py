from os.path import join, dirname
import sys, os, shutil, subprocess
import argparse
from pathlib import Path

ROOT_PATH = subprocess.Popen(
    ['git', 'rev-parse', '--show-toplevel'],
    stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')

TOOL_PATH = str(Path.home()) + '/Z01-Tools/'

if( ROOT_PATH[-9:] == 'Z01-tools'):
    PROJ_PATH = os.path.join(ROOT_PATH, '../')
else:
    PROJ_PATH = os.path.join(ROOT_PATH, 'Projetos')

TOOL_SCRIPT_PATH = os.path.join(TOOL_PATH, 'scripts')
PATH_SIMULATOR = os.path.join(TOOL_PATH, 'Z01-Simulator-rtl')

# Path to vsim  #
PATH_VSIM = os.path.join(os.environ.get('VUNIT_MODELSIM_PATH'), "vsim")

ASSEMBLER_JAR = TOOL_PATH+"/jar/Z01-Assembler.jar"
VMTRANSLATOR_JAR = TOOL_PATH+"/jar/Z01-VMTranslator.jar"

TCL_FILE = "atualizaMemoria.tcl"
TAB = "    "
END = "\n"

######################################################

CDF_ULA_PATH = TOOL_PATH + '/sof/Z011-ULA.cdf'
CDF_Z01_PATH = TOOL_PATH + '/sof/Z011.cdf'

######################################################

CI_GITHUB = True if os.environ.get('GITHUB_WORKFLOW') else False
CI_TRAVIS = True if os.environ.get('TRAVIS') else False
NOTIFY_ENABLE = not (CI_GITHUB or CI_TRAVIS)
NOTIFY_IMAGES  = TOOL_SCRIPT_PATH + '/data/'

######################################################

PROJ_B_NAME = 'Logica Combinacional'
PROJ_C_NAME = 'Unidade Logica Aritmetica'
PROJ_D_NAME = 'Logica Sequencial'
PROJ_E_NAME = 'Assembly'
PROJ_F_NAME = 'Computador'
PROJ_G_NAME = 'Assembler'
PROJ_H_NAME = 'VM'
PROJ_I_NAME = 'VMTranslator'

PROJ_B_PATH = os.path.join(PROJ_PATH, 'B-LogicaCombinacional')
PROJ_C_PATH = os.path.join(PROJ_PATH, 'C-UnidadeLogicaAritmetica')
PROJ_D_PATH = os.path.join(PROJ_PATH, 'D-LogicaSequencial')
PROJ_E_PATH = os.path.join(PROJ_PATH, 'E-Assembly')
PROJ_F_PATH = os.path.join(PROJ_PATH, 'F-Computador')
PROJ_G_PATH = os.path.join(PROJ_PATH, 'G-Assembler')
PROJ_H_PATH = os.path.join(PROJ_PATH, 'H-VM')
PROJ_I_PATH = os.path.join(PROJ_PATH, 'I-VMTranslator')

PROJ_B_TEST = 'testeLogicaCombinacional.py'
PROJ_C_TEST = 'testeULA.py'
PROJ_D_TEST = 'testeLogicaSequencial.py'
PROJ_E_TEST = 'testeAssembly.py'
PROJ_F_TEST = 'testeAssemblyMyCPU.py'
PROJ_G_TEST = 'testeAssemblerMyCPU.py'
PROJ_H_TEST = 'testeVm.py'
PROJ_I_TEST = 'testeVMtranslator.py'

Z01_GUI_PATH = TOOL_PATH+'/Z01-Simulator-GUI/'

sys.path.insert(0,TOOL_SCRIPT_PATH)
sys.path.insert(0,PROJ_B_PATH)
sys.path.insert(0,PROJ_C_PATH)
sys.path.insert(0,PROJ_D_PATH)
sys.path.insert(0,PROJ_E_PATH)
sys.path.insert(0,PROJ_F_PATH)
sys.path.insert(0,PROJ_G_PATH)
sys.path.insert(0,PROJ_H_PATH)
sys.path.insert(0,PROJ_I_PATH)

######################################################

# config file
CONFIG_FILE = "config.txt"

# TST DIR files
TST_DIR = "tst/"

# RAM files
RAM_INIT_FILE     = "_in.mif"
RAM_END_FILE      = "_tst.mif"
RAM_END_SIMU_FILE = "_end.mif"
OUT_SIM_LST = ""

ERRO_NONE = 0
ERRO_ASSEMBLER = 1
ERRO_ASSEMBLER_FILE = 2
ERRO_SIMULATION = 3
ERRO_SIMULATION_TESTE = 4
ERRO_VHDL = 5
ERRO_VHDL_TESTE = 6
ERRO_PROGRAMING = 7

LOG_DB_PASS = 'PASS'
LOG_DB_FAIL = 'FAIL'

######################################################

from report import report
from notificacao import notificacao
from testeVHDL import vhdlScript

try:
    from testeLogicaCombinacional import tstLogiComb
    from testeULA import tstUla
    from testeLogicaSequencial import tstLogiSeq
except:
    print("Erro importando...")

from toMIF import toMIF
from writeSOF import writeSOF
from assembler import *
from writeROM import writeROM
