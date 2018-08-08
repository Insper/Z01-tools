import os

class Config:
    #Path to vsim  #
    PATH_VSIM = os.environ.get('VUNIT_MODELSIM_PATH')

    # Files used on this simulation
    PATH_WORK       = os.path.dirname(os.path.abspath(__file__))+"/../Z01-Simulator-rtl/"
    PATH_DO         = os.path.join(PATH_WORK, "do/sim.do")
    TEMP_IN_RAM_MIF = os.path.join(PATH_WORK, "in/tmpRAM.mif")
    TEMP_IN_ROM_MIF = os.path.join(PATH_WORK, "in/tmpROM.mif")
    OUT_RAM_MEM     = os.path.join(PATH_WORK, "out/RAM.mem")
    OUT_ROM_MEM     = os.path.join(PATH_WORK, "out/ROM.mem")
    OUT_SIM_LST     = os.path.join(PATH_WORK, "out/SIM.lst")

    END = "\n"

    # config file
    CONFIG_FILE = "config.txt"

    # TST DIR files
    TST_DIR = "tst/"

    # RAM files
    RAM_INIT_FILE     = "_in.mif"
    RAM_END_FILE      = "_tst.mif"
    RAM_END_SIMU_FILE = "_end.mif"


