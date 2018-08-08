################################
# Desabilita alguns warnings
################################

set StdArithNoWarnings 1
set StdNumNoWarnings 1
set NumericStdNoWarnings 1

################################
# Recompila todos os arquivod
################################
# RAM16K
vcom -work work Modulos/Dispositivos/RAM/RAM16K.vhd

# ROM
vcom -work work Modulos/Dispositivos/ROM/ROM32K.vhd

#PLL
#vcom -reportprogress 300 -work work Modulos/Dispositivos/PLL/*.vhd
vcom -reportprogress 300 -work work Modulos/Dispositivos/PLL/PLL_sim/PLL.vho

#################################
# Carrega simulação no computador_tb
#################################
# carrega modulo

vsim work.computador_tb

# carrega lista de sinais a serem exportados

do list.do

################################
# carrega wave com a CPU
################################
add wave -position end sim:/computador_tb/c1/MAIN_CPU/*

################################
# Executa simulação
################################

run 1000 ns

################################
# Exporta resultado (list)
################################

write list ./out/SIM.lst

################################
# Exporta memorias
################################
# ROM
mem save -o ./out/ROM.mem -f mti -data binary -addr decimal -startaddress 0 -endaddress 32767 -wordsperline 1 /computador_tb/c1/ROM/altsyncram_component/MEMORY/m_mem_data_a

# RAM
mem save -o ./out/RAM.mem -f mti -data binary -addr decimal -startaddress 0 -endaddress 16383 -wordsperline 1 /computador_tb/c1/MEMORY_MAPED/RAM/altsyncram_component/MEMORY/m_mem_data_a
################################
# Exit
################################

exit







