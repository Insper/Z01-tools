vlib work

#vcom -reportprogress 300 -work work ../../C-LogicaCombinacional/src/rtl/*.vhd
#vcom -reportprogress 300 -work work ../../E-LogicaSequencial/src/rtl/*.vhd
#vcom -reportprogress 300 -work work ../../D-UnidadeLogicaAritmetica/src/rtl/*.vhd

vcom -reportprogress 300 -work work ../src/rtl/*.vhd
#vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/PLL/*.vhd
vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/PLL/PLL_sim/PLL.vho
vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/RAM/*.vho
vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/ROM/*.vhd
vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/Screen/FIFO/*.vhd
vcom -reportprogress 300 -work work ../src/rtl/Dispositivos/Screen/*.vho

vcom -reportprogress 300 -work work ../tests/Computador_tb.vhd
