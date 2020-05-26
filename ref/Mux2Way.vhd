-- Elementos de Sistemas
-- by Luciano Soares
-- Mux2Way.vhd

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity Mux2Way is
	port ( 
			a:   in  STD_LOGIC;
			b:   in  STD_LOGIC;
			sel: in  STD_LOGIC;
			q:   out STD_LOGIC);
end entity;

architecture arch of Mux2Way is

	signal tmp1, tmp2 : STD_LOGIC;

begin

	tmp1 <= a and (not sel);
	tmp2 <= b and sel;
	q <= tmp1 or tmp2;

end architecture;